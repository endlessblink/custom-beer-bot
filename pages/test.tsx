import { useEffect, useState, useCallback } from 'react';
import { config } from '../src/lib/config';

export default function TestPage() {
  const [instanceState, setInstanceState] = useState<any>(null);
  const [groups, setGroups] = useState<any[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [groupData, setGroupData] = useState<any>(null);
  const [error, setError] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [loadingGroups, setLoadingGroups] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [showDebug, setShowDebug] = useState(false);

  const fetchGroups = useCallback(async () => {
    if (instanceState?.stateInstance !== 'authorized') return;
    
    setLoadingGroups(true);
    setError(null);
    try {
      const response = await fetch('/api/whatsapp/getChats');
      const data = await response.json();

      // Filter only group chats
      const groups = (data || [])
        .filter((chat: any) => chat.id && chat.id.includes('@g.us'))
        .map((group: any) => ({
          id: group.id,
          name: group.name || group.id
        }));

      setGroups(groups);
      console.log('Groups:', groups);
    } catch (err: any) {
      console.error('Error fetching groups:', err);
      setError(err);
    } finally {
      setLoadingGroups(false);
    }
  }, [instanceState?.stateInstance]);

  const checkInstanceState = useCallback(async () => {
    try {
      const response = await fetch('/api/whatsapp/getStateInstance');
      const data = await response.json();

      if (data.stateInstance) {
        setInstanceState({ stateInstance: data.stateInstance });
        console.log('Instance state:', data.stateInstance);
      } else {
        throw new Error('Invalid response from API');
      }
    } catch (err: any) {
      console.error('Error:', err);
      setError(err);
      setInstanceState({ stateInstance: 'unauthorized' });
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial state check
  useEffect(() => {
    checkInstanceState();
  }, [checkInstanceState]);

  // Fetch groups when authorized
  useEffect(() => {
    if (instanceState?.stateInstance === 'authorized') {
      fetchGroups();
    }
  }, [instanceState?.stateInstance, fetchGroups]);

  const fetchGroupData = async (groupId: string) => {
    if (!groupId) {
      setError('Please select a group');
      return;
    }

    setError(null);
    setFetching(true);
    try {
      const response = await fetch('/api/whatsapp/getGroupData', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ groupId }),
      });

      const data = await response.json();
      setGroupData(data);
      console.log('Group data:', data);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err);
    } finally {
      setFetching(false);
    }
  };

  if (loading) {
    return <div className="p-4">Checking WhatsApp connection...</div>;
  }

  const isUnauthorized = instanceState?.stateInstance !== 'authorized';

  const ErrorDisplay = ({ error }: { error: any }) => (
    <div className="bg-red-50 border border-red-200 p-4 rounded-lg mb-6">
      <div className="text-red-600 mb-2">{error.error || error.message}</div>
      
      {/* Debug Information Toggle */}
      <div className="mt-2">
        <button
          onClick={() => setShowDebug(!showDebug)}
          className="text-sm text-gray-600 hover:text-gray-800"
        >
          {showDebug ? 'Hide' : 'Show'} Debug Info
        </button>
        
        {showDebug && error.debug && (
          <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
            {JSON.stringify(error.debug, null, 2)}
          </pre>
        )}

        {showDebug && error.details && (
          <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
            {JSON.stringify(error.details, null, 2)}
          </pre>
        )}
      </div>

      {error.message?.includes('not authorized') && (
        <div className="mt-4 text-sm text-gray-600">
          <p className="font-medium">Troubleshooting Steps:</p>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>Verify your Green API credentials in the config file</li>
            <li>Make sure your instance is active in the Green API dashboard</li>
            <li>Try scanning the QR code again</li>
            <li>Check if your WhatsApp is properly connected</li>
          </ol>
        </div>
      )}
    </div>
  );

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">WhatsApp Group Data</h1>
      
      {/* Instance State */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Instance State</h2>
        <div className="space-y-2">
          <p>Status: <span className={`font-semibold ${isUnauthorized ? 'text-red-600' : 'text-green-600'}`}>
            {instanceState?.stateInstance || 'unauthorized'}
          </span></p>
          
          {isUnauthorized && (
            <div className="mt-4 bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <h3 className="font-medium text-yellow-800 mb-2">Authorization Required</h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-yellow-700">
                <li>Go to <a href="https://green-api.com/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Green API Dashboard</a></li>
                <li>Find your instance with ID: {config.whatsapp.idInstance}</li>
                <li>Click on the QR code icon or "Connect" button</li>
                <li>Scan the QR code with your WhatsApp mobile app</li>
                <li>After scanning, click the button below to verify connection</li>
              </ol>
              <button
                onClick={checkInstanceState}
                className="mt-4 bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded text-sm"
              >
                Verify Connection
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Group Selection */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Select WhatsApp Group</h2>
          <button
            onClick={fetchGroups}
            disabled={isUnauthorized || loadingGroups}
            className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded disabled:opacity-50"
          >
            {loadingGroups ? 'Loading...' : 'Refresh Groups'}
          </button>
        </div>

        {loadingGroups ? (
          <p className="text-gray-500">Loading groups...</p>
        ) : groups.length > 0 ? (
          <div className="space-y-4">
            <select
              value={selectedGroupId}
              onChange={(e) => {
                setSelectedGroupId(e.target.value);
                if (e.target.value) {
                  fetchGroupData(e.target.value);
                }
              }}
              className="w-full border rounded px-3 py-2"
              disabled={isUnauthorized}
            >
              <option value="">Select a group</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name || group.id}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <p className="text-gray-500">No groups found. Make sure you're a member of some WhatsApp groups.</p>
        )}
      </div>

      {/* Error Display */}
      {error && <ErrorDisplay error={error} />}

      {/* Group Data Display */}
      {groupData && (
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Group Information</h2>
          <div className="space-y-3">
            <p><span className="font-medium">Name:</span> {groupData.subject}</p>
            <p><span className="font-medium">ID:</span> {groupData.groupId}</p>
            <p><span className="font-medium">Owner:</span> {groupData.owner}</p>
            <p><span className="font-medium">Created:</span> {new Date(groupData.creation * 1000).toLocaleString()}</p>
            {groupData.groupInviteLink && (
              <p><span className="font-medium">Invite Link:</span> {groupData.groupInviteLink}</p>
            )}
            
            <div className="mt-4">
              <h3 className="font-medium mb-2">Participants ({groupData.participants?.length || 0})</h3>
              <div className="grid gap-2">
                {groupData.participants?.map((participant: any) => (
                  <div key={participant.id} className="border p-2 rounded">
                    <p>{participant.id}</p>
                    {participant.isAdmin && <span className="text-sm text-blue-600 ml-2">Admin</span>}
                    {participant.isSuperAdmin && <span className="text-sm text-purple-600 ml-2">Super Admin</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useState, useCallback } from 'react';
import { ScheduleConfig } from './ScheduleConfig';
import { Button } from './ui/button';
import { GroupConfig } from '@/lib/config';
import { WhatsAppAPI } from '@/lib/whatsapp';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Label } from './ui/label';

interface GroupSchedulesProps {
  initialGroups?: GroupConfig[];
  onSaveGroup: (group: GroupConfig) => void;
  onRemoveGroup: (groupId: string) => void;
}

interface WhatsAppGroup {
  id: string;
  name: string;
}

export function GroupSchedules({
  initialGroups = [],
  onSaveGroup,
  onRemoveGroup,
}: GroupSchedulesProps) {
  const [groups, setGroups] = useState<GroupConfig[]>(initialGroups);
  const [availableGroups, setAvailableGroups] = useState<WhatsAppGroup[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  const loadAvailableGroups = useCallback(async () => {
    if (isLoading) {
      console.log('Already loading groups, skipping...');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const api = WhatsAppAPI.getInstance();
      
      // Fetch groups directly - this will internally check authorization
      console.log('Fetching WhatsApp groups...');
      const whatsappGroups = await api.getGroups();
      
      if (!whatsappGroups || whatsappGroups.length === 0) {
        console.log('No groups found');
        setAvailableGroups([]);
        setError('No WhatsApp groups found. Make sure you are an admin of at least one group.');
        return;
      }

      console.log('Available groups:', whatsappGroups);
      
      // Filter out groups that are already added
      const availableGroups = whatsappGroups.filter(
        group => !groups.some(g => g.groupId === group.id)
      );
      console.log('Filtered available groups:', availableGroups);
      
      setAvailableGroups(availableGroups);
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to load groups';
      console.error('Error loading groups:', error);
      setError(errorMessage);
      setAvailableGroups([]);
    } finally {
      setIsLoading(false);
    }
  }, [groups, isLoading]);

  useEffect(() => {
    if (isInitialLoad) {
      loadAvailableGroups();
      setIsInitialLoad(false);
    }
  }, [isInitialLoad, loadAvailableGroups]);

  useEffect(() => {
    setGroups(initialGroups);
  }, [initialGroups]);

  const handleAddGroup = async () => {
    if (!selectedGroupId) {
      setError('Please select a group first');
      return;
    }

    const selectedGroup = availableGroups.find(g => g.id === selectedGroupId);
    if (!selectedGroup) {
      setError('Selected group not found');
      return;
    }

    const newGroup: GroupConfig = {
      groupId: selectedGroup.id,
      name: selectedGroup.name,
      schedules: []
    };

    onSaveGroup(newGroup);
    setSelectedGroupId('');
  };

  const handleTestSummary = async (groupId: string) => {
    try {
      console.log('Generating test summary for group:', {
        groupId,
        groupDetails: groups.find(g => g.groupId === groupId)
      });

      const response = await fetch('/api/test?endpoint=generateTestSummary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          groupId
        })
      });

      const data = await response.json();
      console.log('Test summary API response:', {
        status: response.status,
        data
      });
      
      if (!response.ok) {
        throw new Error(data.error || data.details || 'Failed to generate test summary');
      }

      console.log('Test summary generated successfully:', data);
      alert('Test summary sent successfully!');
    } catch (error: any) {
      console.error('Failed to generate test summary:', {
        error: error.message,
        groupId,
        group: groups.find(g => g.groupId === groupId)
      });
      alert(`Failed to generate test summary: ${error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Add New Group</CardTitle>
          <CardDescription>Select a WhatsApp group to configure automated summaries</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4">
            <div className="grid w-full items-center gap-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="group">WhatsApp Group</Label>
                <Select
                  value={selectedGroupId}
                  onValueChange={setSelectedGroupId}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={isLoading ? "Loading..." : "Select a group"} />
                  </SelectTrigger>
                  <SelectContent>
                    {availableGroups.map((group) => (
                      <SelectItem key={group.id} value={group.id}>
                        {group.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <Button
                onClick={loadAvailableGroups}
                variant="outline"
                disabled={isLoading}
              >
                {isLoading ? 'Loading...' : 'Refresh Groups'}
              </Button>
              <Button
                onClick={handleAddGroup}
                disabled={!selectedGroupId || isLoading}
              >
                Add Group
              </Button>
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {groups.length > 0 && (
        <div className="space-y-4">
          {groups.map((group) => (
            <Card key={group.groupId}>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>{group.name}</CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleTestSummary(group.groupId)}
                    >
                      Test Summary
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => onRemoveGroup(group.groupId)}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <ScheduleConfig
                  schedules={group.schedules}
                  onSchedulesChange={(schedules) => {
                    const updatedGroup = { ...group, schedules };
                    onSaveGroup(updatedGroup);
                  }}
                />
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
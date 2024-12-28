'use client';

import { useState } from 'react';
import { GroupSchedules } from '@/components/GroupSchedules';
import { GroupConfig } from '@/lib/config';
import { storage } from '@/lib/storage';

export default function Home() {
  const [groups, setGroups] = useState<GroupConfig[]>(storage.getGroups());

  const handleSaveGroup = (group: GroupConfig) => {
    const updatedGroups = [...groups, group];
    setGroups(updatedGroups);
    storage.saveGroups(updatedGroups);
  };

  const handleRemoveGroup = (groupId: string) => {
    const updatedGroups = groups.filter(g => g.groupId !== groupId);
    setGroups(updatedGroups);
    storage.saveGroups(updatedGroups);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-8">WhatsApp Bot Configuration</h1>
      <div className="w-full max-w-4xl">
        <GroupSchedules
          initialGroups={groups}
          onSaveGroup={handleSaveGroup}
          onRemoveGroup={handleRemoveGroup}
        />
      </div>
    </main>
  );
}

import React, { useState } from 'react';
import { Button } from './ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { ScheduleConfig as IScheduleConfig, SummaryFrequency } from '../lib/config';
import { WhatsAppAPI } from '../lib/whatsapp';

interface ScheduleConfigProps {
  groupId: string;
  initialConfig?: IScheduleConfig;
  onSave: (config: IScheduleConfig) => void;
}

const DAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];

export function ScheduleConfig({ groupId, initialConfig, onSave }: ScheduleConfigProps) {
  const [config, setConfig] = useState<IScheduleConfig>(() => ({
    frequency: 'daily',
    time: '20:00',
    enabled: true,
    ...initialConfig,
  }));
  const [isTesting, setIsTesting] = useState(false);

  const handleFrequencyChange = (value: SummaryFrequency) => {
    setConfig(prev => ({
      ...prev,
      frequency: value,
      day: value === 'weekly' ? (prev.day || 'SUNDAY') : undefined,
    }));
  };

  const handleTimeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setConfig(prev => ({
      ...prev,
      time: event.target.value,
    }));
  };

  const handleDayChange = (value: string) => {
    setConfig(prev => ({
      ...prev,
      day: value,
    }));
  };

  const handleToggle = () => {
    setConfig(prev => ({
      ...prev,
      enabled: !prev.enabled,
    }));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSave(config);
  };

  const handleTestSummary = async () => {
    setIsTesting(true);
    try {
      if (!groupId) {
        throw new Error('No group ID provided');
      }

      console.log('Sending test summary to group:', { groupId });

      const response = await fetch('/api/test?endpoint=sendTestSummary', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          groupId,
          message: `🧪 *Test Summary Message*\n\nThis is a test message from WhatsApp Summary Bot to verify the connection.\n\n_Sent at: ${new Date().toLocaleString()}_`,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        console.error('Test summary failed:', {
          status: response.status,
          data,
          groupId
        });
        throw new Error(data.error || data.message || 'Failed to send test summary');
      }

      window.alert('Test summary sent successfully!');
    } catch (error: any) {
      console.error('Failed to send test summary:', {
        error: error.message,
        groupId,
        originalError: error
      });
      window.alert(`Failed to send test summary: ${error.message}`);
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white rounded-lg shadow">
      <div className="space-y-2">
        <label className="text-sm font-medium">Summary Frequency</label>
        <Select
          value={config.frequency}
          onValueChange={handleFrequencyChange}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select frequency" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="daily">Daily</SelectItem>
            <SelectItem value="weekly">Weekly</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {config.frequency === 'weekly' && (
        <div className="space-y-2">
          <label className="text-sm font-medium">Day of Week</label>
          <Select
            value={config.day || 'SUNDAY'}
            onValueChange={handleDayChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select day" />
            </SelectTrigger>
            <SelectContent>
              {DAYS.map(day => (
                <SelectItem key={day} value={day}>
                  {day.charAt(0) + day.slice(1).toLowerCase()}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">Time</label>
        <input
          type="time"
          value={config.time}
          onChange={handleTimeChange}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        />
      </div>

      <div className="flex items-center justify-between gap-2">
        <Button
          type="button"
          variant={config.enabled ? 'default' : 'secondary'}
          onClick={handleToggle}
        >
          {config.enabled ? 'Enabled' : 'Disabled'}
        </Button>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleTestSummary}
            disabled={isTesting}
          >
            {isTesting ? 'Sending...' : 'Test Summary'}
          </Button>
          <Button type="submit">Save Schedule</Button>
        </div>
      </div>
    </form>
  );
}

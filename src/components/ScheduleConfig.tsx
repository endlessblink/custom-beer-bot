import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent } from './ui/card';
import { Schedule } from '@/lib/config';

interface ScheduleConfigProps {
  schedules: Schedule[];
  onSchedulesChange: (schedules: Schedule[]) => void;
}

export function ScheduleConfig({ schedules, onSchedulesChange }: ScheduleConfigProps) {
  const [newSchedule, setNewSchedule] = useState<Schedule>({
    frequency: 'daily',
    time: '20:00',
    enabled: true,
    days: ['Monday']
  });

  const handleAddSchedule = () => {
    onSchedulesChange([...schedules, newSchedule]);
    setNewSchedule({
      frequency: 'daily',
      time: '20:00',
      enabled: true,
      days: ['Monday']
    });
  };

  const handleRemoveSchedule = (index: number) => {
    const updatedSchedules = schedules.filter((_, i) => i !== index);
    onSchedulesChange(updatedSchedules);
  };

  const handleUpdateSchedule = (index: number, updates: Partial<Schedule>) => {
    const updatedSchedules = schedules.map((schedule, i) => {
      if (i === index) {
        return { ...schedule, ...updates };
      }
      return schedule;
    });
    onSchedulesChange(updatedSchedules);
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {schedules.map((schedule, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="grid gap-4">
                <div className="flex items-center justify-between">
                  <Label>Enabled</Label>
                  <Switch
                    checked={schedule.enabled}
                    onCheckedChange={(checked) =>
                      handleUpdateSchedule(index, { enabled: checked })
                    }
                  />
                </div>
                <div className="grid gap-2">
                  <Label>Frequency</Label>
                  <Select
                    value={schedule.frequency}
                    onValueChange={(value: 'daily' | 'weekly' | 'custom') =>
                      handleUpdateSchedule(index, { frequency: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label>Time</Label>
                  <Input
                    type="time"
                    value={schedule.time}
                    onChange={(e) =>
                      handleUpdateSchedule(index, { time: e.target.value })
                    }
                  />
                </div>
                {schedule.frequency === 'weekly' && (
                  <div className="grid gap-2">
                    <Label>Day</Label>
                    <Select
                      value={schedule.days?.[0] || 'Monday'}
                      onValueChange={(value) =>
                        handleUpdateSchedule(index, { days: [value] })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(
                          (day) => (
                            <SelectItem key={day} value={day}>
                              {day}
                            </SelectItem>
                          )
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                )}
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleRemoveSchedule(index)}
                >
                  Remove Schedule
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label>Frequency</Label>
              <Select
                value={newSchedule.frequency}
                onValueChange={(value: 'daily' | 'weekly' | 'custom') =>
                  setNewSchedule({ ...newSchedule, frequency: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Time</Label>
              <Input
                type="time"
                value={newSchedule.time}
                onChange={(e) =>
                  setNewSchedule({ ...newSchedule, time: e.target.value })
                }
              />
            </div>
            {newSchedule.frequency === 'weekly' && (
              <div className="grid gap-2">
                <Label>Day</Label>
                <Select
                  value={newSchedule.days?.[0] || 'Monday'}
                  onValueChange={(value) =>
                    setNewSchedule({ ...newSchedule, days: [value] })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(
                      (day) => (
                        <SelectItem key={day} value={day}>
                          {day}
                        </SelectItem>
                      )
                    )}
                  </SelectContent>
                </Select>
              </div>
            )}
            <Button onClick={handleAddSchedule}>Add Schedule</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { parseISO, format, isAfter, isBefore, addDays } from 'date-fns';
import { ScheduleConfig, SummaryFrequency } from './config';

export class SummaryScheduler {
  private schedules: Map<string, ScheduleConfig> = new Map();

  addSchedule(groupId: string, config: ScheduleConfig) {
    this.schedules.set(groupId, config);
  }

  removeSchedule(groupId: string) {
    this.schedules.delete(groupId);
  }

  getNextRunTime(groupId: string): Date | null {
    const schedule = this.schedules.get(groupId);
    if (!schedule || !schedule.enabled) return null;

    const now = new Date();
    const today = format(now, 'yyyy-MM-dd');
    const scheduledTime = parseISO(`${today}T${schedule.time}`);

    if (schedule.frequency === 'daily') {
      if (isAfter(now, scheduledTime)) {
        return parseISO(`${format(addDays(now, 1), 'yyyy-MM-dd')}T${schedule.time}`);
      }
      return scheduledTime;
    }

    // Weekly schedule
    const currentDay = format(now, 'EEEE').toUpperCase();
    const targetDay = schedule.day || 'SUNDAY';
    const daysUntilTarget = this.getDaysUntilTarget(currentDay, targetDay);
    
    const nextRunDate = addDays(now, daysUntilTarget);
    return parseISO(`${format(nextRunDate, 'yyyy-MM-dd')}T${schedule.time}`);
  }

  private getDaysUntilTarget(current: string, target: string): number {
    const days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
    const currentIndex = days.indexOf(current);
    const targetIndex = days.indexOf(target);
    
    if (currentIndex === -1 || targetIndex === -1) {
      throw new Error('Invalid day format');
    }

    let daysUntil = targetIndex - currentIndex;
    if (daysUntil <= 0) {
      daysUntil += 7;
    }
    return daysUntil;
  }

  getSchedule(groupId: string): ScheduleConfig | undefined {
    return this.schedules.get(groupId);
  }

  updateSchedule(groupId: string, updates: Partial<ScheduleConfig>) {
    const current = this.schedules.get(groupId);
    if (current) {
      this.schedules.set(groupId, { ...current, ...updates });
    }
  }
} 
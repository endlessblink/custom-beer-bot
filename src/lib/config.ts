export const config = {
  whatsapp: {
    idInstance: process.env.GREEN_API_ID_INSTANCE || '7105169202',
    apiTokenInstance: process.env.GREEN_API_TOKEN_INSTANCE || 'fcd7e60dde584aa4823949c3032fcad318375231ff1f4df6b4',
    apiUrl: process.env.GREEN_API_URL || 'https://api.green-api.com',
    phoneNumber: '972526784960'
  },
  summarySchedule: {
    daily: {
      defaultTime: "20:00", // Default time for daily summaries
    },
    weekly: {
      defaultTime: "18:00", // Default time for weekly summaries
      defaultDay: "SUNDAY", // Default day for weekly summaries
    },
  },
} as const;

export type SummaryFrequency = 'daily' | 'weekly';

export interface ScheduleConfig {
  groupId: string;
  enabled: boolean;
  frequency: SummaryFrequency;
  time: string;  // 24-hour format HH:mm
  day?: string;  // Required for weekly frequency
  type: 'summary';  // Type of scheduled message
}

export interface GroupConfig {
  groupId: string;
  name?: string;
  schedule?: {
    enabled: boolean;
    interval: number;
    lastRun?: number;
  };
}
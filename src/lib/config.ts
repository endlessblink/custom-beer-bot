export const config = {
  whatsapp: {
    idInstance: process.env.GREEN_API_ID_INSTANCE || '7105169202',
    apiTokenInstance: process.env.GREEN_API_TOKEN_INSTANCE || 'fcd7e60dde584aa4823949c3032fcad318375231ff1f4df6b4',
    apiUrl: process.env.GREEN_API_URL || 'https://api.green-api.com',
    phoneNumber: '972526784960'
  },
  summarySchedule: {
    daily: {
      defaultTime: "20:00",
    },
    weekly: {
      defaultTime: "18:00",
      defaultDay: "SUNDAY",
    },
  },
} as const;

export type SummaryFrequency = 'daily' | 'weekly' | 'custom';

export interface Schedule {
  frequency: SummaryFrequency;
  time: string;  // 24-hour format HH:mm
  enabled: boolean;
  days?: string[];  // Required for weekly frequency
}

export interface GroupConfig {
  groupId: string;
  name: string;
  schedules: Schedule[];
}
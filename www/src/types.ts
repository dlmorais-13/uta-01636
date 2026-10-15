export type SimulationFilters = {
  type: 'location' | 'management' | 'text',
  name: string,
  description?: string,
  column?: string,
  value?: string,
  options?: string[]
}

export type SimulationParameters = {
  type: 'target',
  name: string,
  description?: string,
  column?: string,
  source?: ValueCount[],
  options?: LabelValue[],
  optionPercentage?: Record<string, number>
  value?: string,
  target?: number,
}

export type ValueCount = {
  value: string,
  count: number
}

export type LabelValue = {
  label: string,
  value: string
}

export type Job = {
  objectId?: number,
  name: string,
  params: unknown,
  createDate: Date,
  startDate?: Date,
  endDate?: Date,
  status: JobStatus,
  executorName?: string
}

export type JobStatus = "CREATED" | "CLAIMED" | "RUNNING" | "COMPLETED" | "FAILED";

export type Job = {
  id: string
  payload: string
  attempts: number
}

export class JobQueue {
  private completed = new Set<string>()
  constructor(private pending: Job[] = []) {}

  claim(): Job | undefined {
    return this.pending.shift()
  }

  requeue(job: Job): void {
    this.pending.push({
      ...job,
      attempts: job.attempts + 1,
    })
  }

  acknowledge(job: Job): void {
    this.completed.add(job.id)
  }
}

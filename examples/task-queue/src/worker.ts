import { JobQueue } from './queue'

type Handler = (payload: string) => Promise<string>
type Save = (id: string, value: string) => Promise<void>

export async function runNext(
  queue: JobQueue,
  handle: Handler,
  save: Save,
): Promise<void> {
  const job = queue.claim()
  if (!job) return

  let result: string
  try {
    result = await handle(job.payload)
  } catch (error) {
    if (job.attempts >= 2) throw error
    queue.requeue(job)
    return
  }

  await save(job.id, result)
  queue.acknowledge(job)
}

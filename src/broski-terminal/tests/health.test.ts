import { expect, test } from 'vitest'
import { GET } from '../app/api/health/route'

test('Health Check API returns 200 and healthy status', async () => {
  const response = await GET()
  const body = await response.json()

  expect(response.status).toBe(200)
  expect(body).toEqual({ status: 'healthy' })
})

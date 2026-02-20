import { test, expect } from '@playwright/test';

test.describe('System Health & Basic Checks', () => {
  
  test('Health Check API returns 200 and healthy status', async ({ request }) => {
    const response = await request.get('/api/health');
    
    // Verify status code
    expect(response.status()).toBe(200);
    
    // Verify response body
    const body = await response.json();
    expect(body).toEqual({ status: 'healthy' });
  });

  // Placeholder for Auth test since no auth implementation was found
  test.skip('Basic Auth check (Skipped: Auth not implemented yet)', async ({ page }) => {
    await page.goto('/');
    // Expect redirection to login or similar
    // await expect(page).toHaveURL(/.*login/);
  });
});

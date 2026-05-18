import { test, expect } from '@playwright/test'

test('guest is redirected from history to login', async ({ page }) => {
  await page.goto('/history')
  await expect(page.getByRole('heading', { name: 'Вход' })).toBeVisible()
})

test('external api error is shown gracefully', async ({ page }) => {
  await page.route('**/api/external/sources**', async (route) => {
    await route.fulfill({
      status: 502,
      contentType: 'application/json',
      body: JSON.stringify({ code: 'EXTERNAL_API_ERROR', message: 'failed to load external sources' }),
    })
  })
  await page.goto('/')
  await page.getByPlaceholder('Например: базы данных').fill('python')
  await page.getByRole('button', { name: 'Подобрать источники' }).click()
  await expect(page.getByText(/EXTERNAL_API_ERROR/i)).toBeVisible()
})

/**
 * fetch-hostmonit-ipv6.js
 * 抓取 https://stock.hostmonit.com/CloudFlareYesV6 页面上的 IPv6 CIDR
 * 输出到 stdout（由 workflow 重定向到 ipv6.txt）
 */
import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setUserAgent(
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
  );

  const url = 'https://stock.hostmonit.com/CloudFlareYesV6';
  console.error('Fetching IPv6 ranges from hostmonit...');
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

  const content = await page.evaluate(() => document.body.innerText);
  await browser.close();

  const ranges = content
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => /^[0-9a-fA-F:]+(?:\/\d{1,3})?$/.test(l));

  if (!ranges.length) {
    console.error('❌ 未获取到任何 IPv6 地址段');
    process.exit(1);
  }

  const unique = [...new Set(ranges)].sort();
  console.log(unique.join('\n'));
})();

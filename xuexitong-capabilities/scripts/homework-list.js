// 在作业列表页执行（把作业 iframe 的 src 当顶层 URL 打开后）。
// 返回作业标题/状态/workId/answerId；不返回 enc 等会话令牌。
(() => {
  return [...document.querySelectorAll('li[onclick*="goTask"]')].map(li => {
    const label = li.getAttribute('aria-label') || '';
    const title = (li.querySelector('p')?.innerText || label.split(';')[0] || '').trim();
    const status = (label.split(';')[1] || '').trim();
    let workId = '', answerId = '';
    try {
      const q = new URL(li.getAttribute('data') || '').searchParams;
      workId = q.get('workId') || '';
      answerId = q.get('answerId') || '';
    } catch (e) {}
    return { title, status, workId, answerId };
  }).filter(x => x.title);
})()

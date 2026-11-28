// 在考试列表页执行；当前仅做通用读取，具体字段待逐课验证。
// 若 iframe 跨域，先把 iframe src 当顶层 URL 打开。
(() => {
  const text = (document.body.innerText || '').replace(/\r/g, '');
  const links = [...document.querySelectorAll('a')].map(a => ({
    text: (a.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 100),
    href: a.getAttribute('href') || ''
  })).filter(x => x.text && !x.href.startsWith('javascript:'));
  return { text: text.slice(0, 6000), links };
})()

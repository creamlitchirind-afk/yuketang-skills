// 在课程“错题集”页执行；只读列表，不点答题。
// 空页返回 rows: []；有题时的行结构仍需逐课验证。
(() => {
  const f = document.querySelector('#frame_content-ctj');
  const doc = f && f.contentDocument ? f.contentDocument : document;
  const text = (doc.body.innerText || '').replace(/\r/g, '');
  const empty = /暂无错题/.test(text);
  const rows = empty ? [] : [...doc.querySelectorAll('[class*="question"], [class*="que"]')].map(li => ({
    text: (li.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 180),
    onclick: li.querySelector('[onclick]')?.getAttribute('onclick')?.slice(0, 200) || ''
  })).filter(x => x.text);
  return { empty, text: text.slice(0, 6000), rows };
})()

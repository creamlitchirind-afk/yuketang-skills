// 在课程“章节”页执行；返回章/节/任务点层级与文本。
(() => {
  const f = [...document.querySelectorAll('iframe')].find(x => x.id === 'frame_content-zj' || x.contentDocument);
  const doc = f && f.contentDocument ? f.contentDocument : document;
  return {
    summary: ((doc.body.innerText || '').match(/已完成任务点[:：]?\s*\d+\s*\/\s*\d+/) || [''])[0],
    text: (doc.body.innerText || '').slice(0, 8000),
    links: [...doc.querySelectorAll('a')].map(a => ({
      text: (a.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 120),
      href: a.getAttribute('href') || ''
    })).filter(x => x.text)
  };
})()

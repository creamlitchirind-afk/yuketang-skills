// 在课程“自测”页执行；读取全部自测列表。
// 返回标题、题量；不触发 goTest()，不进入答题。
(() => {
  const f = document.querySelector('#frame_content-zc');
  const doc = f && f.contentDocument ? f.contentDocument : document;
  return [...doc.querySelectorAll('li')].map(li => {
    const title = (li.querySelector('.right-content .overHidden2')?.innerText || '').trim();
    const count = (li.querySelector('.status')?.innerText || '').trim();
    const onclick = li.querySelector('[onclick]')?.getAttribute('onclick') || '';
    const m = onclick.match(/goTest\(['"](\d+)['"],(\d+),(\d+)/);
    return { title, count, courseId: m ? m[1] : '', examId: m ? m[2] : '', testId: m ? m[3] : '', onclick: onclick.slice(0, 200) };
  }).filter(x => x.title);
})()

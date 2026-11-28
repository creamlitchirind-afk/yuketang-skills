// 在学习记录页执行（把学习记录 iframe 的 src 当顶层 URL 打开后）。
// 返回关键统计 + 原文，避免依赖单一选择器。
(() => {
  const text = (document.body.innerText || '').replace(/\r/g, '');
  const task = text.match(/章节任务点[\s\S]{0,80}?(\d+)\s*\/\s*(\d+)/);
  const att = text.match(/(\d+)\s*出勤\s*(\d+)\s*缺勤/);
  const rank = text.match(/(\d+)\s*名\s*当前排名/);
  const rate = text.match(/出勤率\s+([\d.]+%)/);
  return {
    chapter_task: task ? { done: task[1], total: task[2] } : null,
    attendance: att ? { present: Number(att[1]), absent: Number(att[2]) } : null,
    rank: rank ? rank[1] : '',
    attendance_rate: rate ? rate[1] : '',
    text: text.slice(0, 6000)
  };
})()

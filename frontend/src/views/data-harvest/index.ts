export function getEmotionEmoji(score = 1) {
  // 1-10分: 😭 (崩溃/极度悲伤)
  // 11-20分: 😩 (痛苦/绝望)
  // 21-30分: 😞 (沮丧/失落)
  // 31-40分: 😔 (忧郁/消沉)
  // 41-50分: 😐 (中性/无感)
  // 51-60分: 🙂 (勉强接受)
  // 61-70分: 😌 (平和/释然)
  // 71-80分: 😊 (愉悦/满意)
  // 81-90分: 😄 (开心/兴奋)
  // 91-95分: 🤩 (非常激动/惊艳)
  // 96-100分: 🎉💖 (极度喜悦/庆典级快乐)
  if (score <= 10) {
    return "😭";
  } else if (score <= 20) {
    return "😩";
  } else if (score <= 30) {
    return "😞";
  } else if (score <= 40) {
    return "😔";
  } else if (score <= 50) {
    return "😐";
  } else if (score <= 60) {
    return "🙂";
  } else if (score <= 70) {
    return "😌";
  } else if (score <= 80) {
    return "😊";
  } else if (score <= 90) {
    return "😄";
  } else if (score <= 95) {
    return "🤩";
  } else {
    return "🎉💖";
  }
}

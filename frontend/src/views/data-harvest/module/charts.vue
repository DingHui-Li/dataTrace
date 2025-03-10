<template>
  <div class="charts" v-if="list.length">
    <div class="title">4-图表分析</div>
    <div class="label">关键词</div>
    <div class="chart word-chart" ref="wordChartEl" :style="`height:${(wordChartEl?.clientWidth) / 2}px`"></div>
    <div class="label">情绪趋势</div>
    <div class="chart" ref="lineChartEl" :style="`height:${lineChartEl?.clientWidth / 2}px`"></div>
    <div class="label">数量趋势</div>
    <div class="chart" ref="barChartEl" :style="`height:${barChartEl?.clientWidth / 2}px`"></div>
    <div class="label" style="margin-bottom:0">主题分布</div>
    <div class="chart" ref="radarChartEl" :style="`height:${radarChartEl?.clientWidth}px`"></div>
  </div>
</template>
<script setup lang="ts">
import { computed, shallowRef, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts';
import WordCloud from 'wordcloud'
import { list } from '@/store/data-analyze'
import { handleUpdate } from '../components/panel.ts'
import { getEmotionEmoji } from '../index'

const wordChartEl = ref()

const lineChartEl = ref()
const lineChartIns = shallowRef()

const barChartEl = ref()
const barChartIns = shallowRef()

const radarChartEl = ref()
const radarChartIns = shallowRef()
let timer: any;

watch(list, () => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    nextTick(() => {
      renderWordCloud()
      lineChartIns.value = echarts.init(lineChartEl.value, {}, { locale: 'ZH' })
      renderLineChart()
      barChartIns.value = echarts.init(barChartEl.value, {}, { locale: 'ZH' })
      renderBarChart()
      radarChartIns.value = echarts.init(radarChartEl.value, {}, { locale: 'ZH' })
      renderRadarChart()
    })
  }, 100);
})

const showList = computed(() => {
  return list.value.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})
const topicData = computed(() => {
  let t: any = {}
  list.value.forEach(item => {
    item.topic?.split('/').forEach((topic: any) => {
      t[topic] = (t[topic] || 0) + 1
    })
  })
  return t
})
const keywordMap = computed(() => {
  let t: any = {}
  list.value.forEach(item => {
    item.keywords?.split('/').forEach((word: any) => {
      t[word] = (t[word] || 0) + 1
    })
  })
  console.log(Object.keys(t).length)
  return t
})

function renderWordCloud() {
  let max = 0
  let min = 0
  console.log(keywordMap.value['科技美学'])
  console.log(keywordMap.value['抽奖'])
  Object.keys(keywordMap.value).forEach((word: any) => {
    max = Math.max(keywordMap.value[word], max)
    min = Math.min(keywordMap.value[word], min)
  })
  WordCloud(wordChartEl.value, {
    // minSize: 12,
    shape: "square",
    shuffle: true,
    backgroundColor: "transparent",
    color: "#ffffff",
    shrinkToFit: true,
    minSize: 5,
    list: Object.keys(keywordMap.value).map(word => {
      return [
        word,
        keywordMap.value[word] - min / (max - min) * (30 - 12) + 12
      ]
    })
  })
}

function renderLineChart() {
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line'
      },
      formatter: (params: any) => {
        return `${params[0].name}:${getEmotionEmoji(params[0].data)}`
      },
      extraCssText: "background:rgba(0,0,0,0.8);padding:5px 10px;border-radius:10px;color:#fff;font-size:12px;border:1px solid rgba(255,255,255,0.1)"
    },
    grid: {
      show: false,
      height: (lineChartEl.value?.clientHeight - 30) || "88%",
      width: (lineChartEl.value?.clientWidth - 25) || '95%',
      top: 10,
      left: 25
    },
    visualMap: {
      show: false,
      pieces: [
        {
          gt: 1,
          lte: 10,
          color: '#2F3361'
        },
        {
          gt: 10,
          lte: 20,
          color: '#4A4C8C'
        },
        {
          gt: 20,
          lte: 30,
          color: '#6B6DB2'
        },
        {
          gt: 30,
          lte: 40,
          color: '#9092C2'
        },
        {
          gt: 40,
          lte: 50,
          color: '#A8A9B8'
        },
        {
          gt: 50,
          lte: 60,
          color: '#B3C4A4'
        },
        {
          gt: 60,
          lte: 70,
          color: '#9CD08F'
        },
        {
          gt: 70,
          lte: 80,
          color: '#FFD56E'
        },
        {
          gt: 80,
          lte: 90,
          color: '#FFA447'
        },
        {
          gt: 90,
          lte: 100,
          color: '#FF6B8B'
        }
      ],
      outOfRange: {
        color: '#999'
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: [25, 0],
      axisTick: {
        show: false,
        lineStyle: {
          color: "rgba(0,0,0,0.3)"
        }
      },
      axisLine: {
        lineStyle: {
          color: "rgba(0,0,0,0.1)"
        }
      },
      axisLabel: {
        fontSize: 8,
        color: "#999999"
      },
      data: showList.value.map((item: any) => item.date)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 8,
        color: "#999999",
        formatter: function (value: any) {
          return value >= 1000 ? ((value / 1000).toFixed(1) + "k") : value;
        },
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.03)"
        }
      },
      axisTick: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.3)"
        }
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.1)"
        }
      },
    },
    series: [
      {
        type: 'line',
        symbol: 'none',
        // smooth: true,
        lineStyle: {
          width: 1,
        },
        data: showList.value.map((item: any) => item.emotion_score)
      }
    ]
  }
  lineChartIns.value?.setOption(option)
  handleUpdate()
}

function renderBarChart() {
  const option = {
    tooltip: {
      trigger: 'axis',
      // position: function (pt) {
      //   return [pt[0], '10%'];
      // },
      axisPointer: {
        type: 'line'
      },
      formatter: (params: any) => {
        return `${params[0].name}: ${params[0].data}条内容`
      },
      extraCssText: "background:rgba(0,0,0,0.8);padding:5px 10px;border-radius:10px;color:#fff;font-size:12px;border:1px solid rgba(255,255,255,0.1)"
    },
    grid: {
      show: false,
      height: lineChartEl.value.clientHeight - 60 || "75%",
      width: lineChartEl.value.clientWidth - 40 || '85%',
      top: 20,
      left: 30
    },
    xAxis: {
      axisTick: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.3)"
        }
      },
      axisLine: {
        lineStyle: {
          color: "rgba(0,0,0,0.1)"
        }
      },
      axisLabel: {
        // rotate: 45,
        fontSize: 8,
        color: "#999999",
        // formatter: function (value: any) {
        //   return new Date(value).format('yy/M/d');
        // },
      },
      data: showList.value.map((item: any) => item.date)
    },
    yAxis: {
      type: 'value',
      // show: false,
      splitLine: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.03)"
        }
      },
      axisTick: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.3)"
        }
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: "rgba(0,0,0,0.1)"
        }
      },
      axisLabel: {
        fontSize: 8,
        color: "#999999",
      }
    },
    series: [
      {
        type: 'bar',
        symbol: 'none',
        color: '#7879ef',
        large: true,
        data: showList.value.map(item => item.urls.split('\n').length),
      }
    ]
  }
  barChartIns.value?.setOption(option)
  handleUpdate()
}

function renderRadarChart() {
  let max = 0
  Object.keys(topicData.value).forEach((topic: any) => {
    max = Math.max(topicData.value[topic], max)
  })
  const option = {
    tooltip: {
      extraCssText: "color:#fff;background:rgba(0,0,0,0.8);padding:5px 10px;border-radius:10px;color:#fff;font-size:12px;border:1px solid rgba(255,255,255,0.1)"
    },
    radar: {
      shape: 'circle',
      indicator:
        Object.keys(topicData.value).map((topic: any) => {
          return { name: topic, max }
        }),
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      axisName: {
        fontSize: 10,
        color: "#999999"
      },
      splitArea: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255,255,255,0.1)'
        }
      },
    },
    series: [
      {
        type: 'radar',
        symbol: 'none',
        lineStyle: {
          width: 1,
          opacity: 0.5
        },
        areaStyle: {
          opacity: 0.15
        },
        data: [
          {
            value: Object.keys(topicData.value).map((topic: any) => {
              return topicData.value[topic] || 0
            }),
          }
        ]
      }
    ]
  }
  radarChartIns.value?.setOption(option)
  handleUpdate()
}
</script>
<style lang="less" scoped>
.charts {
  padding: 15px;
  user-select: none;

  .label {
    font-size: 12px;
    color: #999;
    margin-top: 25px;
    margin-bottom: 10px;
  }

  .word-chart {
    &:deep(span) {
      cursor: pointer;
      opacity: 0.8;
    }
  }
}
</style>
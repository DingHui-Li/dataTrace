<template>
  <div class="calendar-chart">
    <div v-if="showChart" class="chart" ref="calendarChartEl" :style="`height:${yearList.length * 180}px`"></div>
  </div>
  <el-dialog class="calendar-chart-popup" v-model='popup.show' append-to-body>
    <div class="popup">
      <div class="date">{{ popup.data.date }}</div>
      <div class="emoji">
        <span>{{ popup.data.emotion_desc }}</span>
        {{ getEmotionEmoji(popup.data.emotion_score) }}
      </div>
      <div class="summary">
        {{ popup.data.summary }}
      </div>
      <div class="topic">#{{ popup.data.topic }}</div>
      <div class="topic">关键词：{{ popup.data.keywords }}</div>
      <div class="urls">
        <el-tag class='url' v-for="item in popup.data.urls.split('\n')" @click='openUrl(item)'>{{ item }}</el-tag>
      </div>
      <div style="text-align: right;">
        <div class='btn' @click="popup.show = false">关闭</div>
      </div>
    </div>
  </el-dialog>
</template>
<script setup lang="ts">
import { computed, shallowRef, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts';
import { list } from '@/store/data-analyze'
import { handleUpdate } from './panel.ts'
import { getEmotionEmoji } from '../index'

const calendarChartEl = ref()
const calendarChartIns = shallowRef()
const popup = ref<{ show: Boolean, data: any }>({
  show: false,
  data: {}
})
const showChart = ref(true)

watch(list, () => {
  nextTick(() => {
    refreshChart().then(() => {
      calendarChartIns.value = echarts.init(calendarChartEl.value, {}, { locale: 'ZH' })
      calendarChartIns.value.on('click', (params: any) => {
        popup.value = {
          show: true,
          data: params.data[1]
        }
      })
      renderCalendarChart()
    })
  })
}, { immediate: true, deep: true })

const yearList = computed(() => {
  let t: any = {}
  list.value.forEach((item: any) => {
    let year = new Date(item.date).getFullYear()
    t[year] = 1
  })
  return Object.keys(t).sort((a, b) => Number(b) - Number(a))
})

function openUrl(url: string) {
  window.open(url, '_blank')
}
function refreshChart() {
  return new Promise(resolve => {
    showChart.value = false
    nextTick(() => {
      showChart.value = true
      resolve(true)
    })
  })
}

function renderCalendarChart() {
  const option = {
    visualMap: {
      show: false,
      min: 0,
      max: 50,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      top: 'top',
      inRange: {
        color: ['#7879ef30', '#7879ef'],
        opacity: 0
      }
    },
    calendar:
      yearList.value?.map((year, i) => {
        return {
          range: year,
          top: 180 * i + 20,
          left: 60,
          cellSize: ['auto', 20],
          splitLine: {
            show: true,
            lineStyle: {
              color: "rgba(255,255,255,0.05)"
            }
          },
          itemStyle: {
            borderColor: "rgba(255,255,255,0.01)",
            color: "transparent"
          },
          dayLabel: {
            color: "#99999990",
            fontSize: 10
          },
          monthLabel: {
            color: "#99999990",
            fontSize: 10
          },
          yearLabel: {
            fontSize: 14,
            color: "#999999"
          }
        }
      }),
    series:
      yearList.value.map((year, i) => {
        return {
          type: 'scatter',
          coordinateSystem: 'calendar',
          calendarIndex: i,
          data: getYearData(year.toString()),
          label: {
            show: true,
            formatter: function (params: any) {
              let emotion_score = params.value[1].emotion_score;
              return getEmotionEmoji(emotion_score);
            },
            color: '#000'
          },
        }
      })
  }
  calendarChartIns.value?.setOption(option)
  handleUpdate()
}
function getYearData(year = '2025') {
  let t: Array<Array<any>> = []
  list.value.forEach((item: any) => {
    if (item.date.includes(year)) {
      t.push([item.date, item])
    }
  })
  return t
}
</script>
<style lang="less">
.calendar-chart-popup {
  background-color: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  border-radius: 10px;
  padding: 0;
  transition: all .3s;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 80%;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent);
  }

  .el-dialog__header {
    display: none;
  }
}

.popup {
  position: relative;
  padding: 15px;
  user-select: none;

  .date {
    color: #fff;
    font-size: 18px;
    font-weight: bold;
  }

  .emoji {
    position: absolute;
    display: flex;
    align-items: center;
    top: 5px;
    right: 5px;
    font-size: 30px;

    span {
      color: #999;
      font-size: 14px;
      margin-right: 5px;
    }
  }

  .summary {
    margin-top: 15px;
    color: #fff;
  }

  .topic {
    margin-top: 10px;
  }

  .urls {
    margin-top: 10px;

    .url {
      background-color: rgba(255, 255, 255, 0.07);
      border: none;
      color: #999;
      cursor: pointer;
      margin-bottom: 5px;
      margin-right: 5px;

      &:hover {
        opacity: 0.8;
      }
    }
  }

  .btn {
    display: inline-block;
    margin-top: 20px;
    font-size: 14px;
    padding: 6px 20px;
    border: 1px solid #ffffff30;
    border-radius: 10px;
    width: fit-content;
    cursor: pointer;
    color: #fff;

    &:hover {
      opacity: 0.8;
    }
  }
}
</style>
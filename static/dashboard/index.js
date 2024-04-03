const logoBtn = document.querySelector(".nav-logo");
const sidebar = document.querySelector(".sidebar");
const starOff = document.querySelectorAll(".star-off");
const starOn = document.querySelectorAll(".star-on");
const navHighlight = document.querySelectorAll(".nav-link");
const sidebarMediaQuery = window.matchMedia("(max-width: 980px)");


logoBtn.onclick = () => {
  sidebar.classList.toggle("active");
  if (sidebar.classList.contains("active")) {
    for (var i = 0; i < navHighlight.length; i++) {
      navHighlight[i].classList.remove("highlight");
    }
  } else {
    for (var i = 0; i < navHighlight.length; i++) {
      navHighlight[i].classList.add("highlight");
    }
  }
}


for (let i = 0; i < starOff.length; i++) {
  starOff[i].addEventListener("click", function () {
    starOff[i].classList.toggle("active");
    if (starOff[i].classList.contains("active")) {
      starOn[i].classList.add("active");
    } else {
      starOn[i].classList.remove("active");
    }
  })
};



function handleSidebarToggle(){
  if (sidebarMediaQuery.matches) {
    sidebar.classList.add("active");
  } else {
    sidebar.classList.remove("active");
  }
  window.addEventListener("resize",()=>{
  if (sidebarMediaQuery.matches) {
    sidebar.classList.add("active");
  } else {
    sidebar.classList.remove("active");
  }
})

}

handleSidebarToggle();

// APEXCHART
var options = {
  series: [{
  name: 'series1',
  data: [31, 40, 28, 51, 42, 109, 100]
}, {
  name: 'series2',
  data: [11, 32, 45, 32, 34, 52, 41]
}],
  chart: {
  height: 200,
  type: 'chart'
},
dataLabels: {
  enabled: false
},
stroke: {
  curve: 'smooth'
},
xaxis: {
  type: 'datetime',
  categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
},
tooltip: {
  x: {
    format: 'dd/MM/yy HH:mm'
  },
},
};

var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();
// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function (n, prec) {
            var k = Math.pow(10, prec);
            return '' + Math.round(n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

// Area Chart Example
// var ctx = document.getElementById("myAreaChart");
// var myLineChart = new Chart(ctx, {
//     type: 'line',
//     data: {
//         labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
//         datasets: [{
//             label: "Value ",
//             lineTension: 0.3,
//             backgroundColor: "rgba(78, 115, 223, 0.05)",
//             borderColor: "rgba(78, 115, 223, 1)",
//             pointRadius: 3,
//             pointBackgroundColor: "rgba(78, 115, 223, 1)",
//             pointBorderColor: "rgba(78, 115, 223, 1)",
//             pointHoverRadius: 3,
//             pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
//             pointHoverBorderColor: "rgba(78, 115, 223, 1)",
//             pointHitRadius: 10,
//             pointBorderWidth: 2,
//             data: [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000],
//         }],
//     },
//     options: {
//         maintainAspectRatio: false,
//         layout: {
//             padding: {
//                 left: 10,
//                 right: 25,
//                 top: 25,
//                 bottom: 0
//             }
//         },
//         scales: {
//             xAxes: [{
//                 time: {
//                     unit: 'date'
//                 },
//                 gridLines: {
//                     display: false,
//                     drawBorder: false
//                 },
//                 ticks: {
//                     maxTicksLimit: 7
//                 }
//             }],
//             yAxes: [{
//                 ticks: {
//                     maxTicksLimit: 5,
//                     padding: 10,
//                     // Include a dollar sign in the ticks
//                     callback: function (value, index, values) {
//                         return '$' + number_format(value);
//                     }
//                 },
//                 gridLines: {
//                     color: "rgb(234, 236, 244)",
//                     zeroLineColor: "rgb(234, 236, 244)",
//                     drawBorder: false,
//                     borderDash: [2],
//                     zeroLineBorderDash: [2]
//                 }
//             }],
//         },
//         legend: {
//             display: false
//         },
//         tooltips: {
//             backgroundColor: "rgb(255,255,255)",
//             bodyFontColor: "#858796",
//             titleMarginBottom: 10,
//             titleFontColor: '#6e707e',
//             titleFontSize: 14,
//             borderColor: '#dddfeb',
//             borderWidth: 1,
//             xPadding: 15,
//             yPadding: 15,
//             displayColors: false,
//             intersect: false,
//             mode: 'index',
//             caretPadding: 10,
//             callbacks: {
//                 label: function (tooltipItem, chart) {
//                     var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
//                     return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
//                 }
//             }
//         }
//     }
// });


make_chart_from_csv("/static/angles.csv")

function make_chart_from_csv(csv_path) {
    d3.csv(csv_path).then(make_chart)
    return 0
}

function make_chart(data) {
    console.log(data)
    columns = d3.keys(data[0])
    console.log(columns)
    columns.forEach(column => {
        var frame_range = []
        for (i = 0; i < data.length; i++) {
            var frame_num = (data[i])["Frame Number"]
            frame_range.push(frame_num)
        }
        // console.log(frame_range)
        var y_axis = []
        for (i = 0; i < data.length; i++) {
            var curr_data = (data[i])[column]
            y_axis.push(curr_data)
        }
        console.log(y_axis)
        if (column == columns[0])
            return;
        var charts_node = document.getElementById('Charts')
        var canvas_tag = document.createElement("canvas")
        canvas_tag.setAttribute("id", column + "_graph")

        var div_wrapper_for_canvas = document.createElement('div')
        div_wrapper_for_canvas.setAttribute('class', 'chart-bar')
        div_wrapper_for_canvas.appendChild(canvas_tag)

        var div_card_body = document.createElement('div')
        div_card_body.setAttribute('class', 'card-body')
        div_card_body.appendChild(div_wrapper_for_canvas)

        var h6_tag = document.createElement('h6')
        h6_tag.setAttribute('class', 'm-0 font-weight-bold text-primary')
        h6_tag.innerText = column + ' Graph'

        var card_header_div_tag = document.createElement('div')
        card_header_div_tag.setAttribute('class', 'card-header py-3')
        card_header_div_tag.appendChild(h6_tag)

        var card_shadow_div = document.createElement('div')
        card_shadow_div.setAttribute('class', 'card shadow mb-4')

        card_shadow_div.appendChild(card_header_div_tag)
        card_shadow_div.appendChild(div_card_body)

        charts_node.appendChild(card_shadow_div)
        // var ctx = document.getElementById('our_area_chart')
        var myLineChart = new Chart(canvas_tag, {
            type: 'line',
            data: {
                labels: frame_range,
                datasets: [{
                    label: "Value ",
                    lineTension: 0.3,
                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                    borderColor: "rgba(78, 115, 223, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointBorderColor: "rgba(78, 115, 223, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: y_axis,
                }],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        time: {
                            unit: 'date'
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 7
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            maxTicksLimit: 5,
                            padding: 10,
                            // Include a dollar sign in the ticks
                            callback: function (value, index, values) {
                                return number_format(value);
                            }
                        },
                        gridLines: {
                            color: "rgb(234, 236, 244)",
                            zeroLineColor: "rgb(234, 236, 244)",
                            drawBorder: false,
                            borderDash: [2],
                            zeroLineBorderDash: [2]
                        }
                    }],
                },
                legend: {
                    display: false
                },
                tooltips: {
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    intersect: false,
                    mode: 'index',
                    caretPadding: 10,
                    callbacks: {
                        label: function (tooltipItem, chart) {
                            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                            return datasetLabel + number_format(tooltipItem.yLabel);
                        }
                    }
                }
            }
        });


    })
}

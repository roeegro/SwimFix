// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

var current_img_path = '';


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

function make_chart_from_csv(csv_path) {
    let splited_by_slash = csv_path.split('/')
    let name_with_extension = splited_by_slash[splited_by_slash.length - 1]
    csv_name = name_with_extension.split('.')[0]
    d3.csv(csv_path).then(make_chart.bind(csv_name, csv_name))
    return 0
}

function make_chart(csv_name, data) {
    columns = d3.keys(data[0])
    columns.forEach(column => {
        if (column == "" || column == "Frame Number")
            return;
        var frame_range = []
        // Load frame Numberes
        for (i = 0; i < data.length; i++) {
            var frame_num = (data[i])["Frame Number"]
            frame_range.push(frame_num)
        }
        // Get the match body part keypoint from the other side of the body (E.G if we have RShoulder, we will match it with LShoulder)
        var column_prefix = column[0]
        var body_part_name = column.slice(1)
        var match_keypoint_column = body_part_name
        var should_plot_multiple_graphs = false
        var body_sides = []
        body_sides.push('R')
        body_sides.push('L')
        if (body_sides.indexOf(column_prefix) != -1) {
            match_keypoint_column = body_sides[1 + (body_sides.indexOf(column_prefix) % 2)] + body_part_name
            should_plot_multiple_graphs = true
        }

        var charts_node = document.getElementById('Charts')
        var canvas_tag = document.createElement("canvas")
        var canvas_id = column + " graph"
        if (should_plot_multiple_graphs == true) {
            canvas_tag.setAttribute("id", body_part_name + ' Graph from csv : ' + csv_name)
            canvas_id = body_part_name + ' Graph from csv : ' + csv_name
        } else {
            canvas_tag.setAttribute("id", column + ' Graph from csv : ' + csv_name)
            canvas_id = column + ' Graph from csv : ' + csv_name
        }

        var div_wrapper_for_canvas = document.createElement('div')
        div_wrapper_for_canvas.setAttribute('class', 'chart-area')
        div_wrapper_for_canvas.appendChild(canvas_tag)

        var div_card_body = document.createElement('div')
        div_card_body.setAttribute('class', 'cardliron-body')
        div_card_body.appendChild(div_wrapper_for_canvas)

        var h6_tag = document.createElement('h6')
        h6_tag.setAttribute('class', 'm-0 font-weight-bold text-primary')
        if (should_plot_multiple_graphs == true) {
            h6_tag.innerText = body_part_name + ' Graph from csv : ' + csv_name
        } else {
            h6_tag.innerText = column + ' Graph from csv : ' + csv_name
        }

        var card_header_div_tag = document.createElement('div')
        card_header_div_tag.setAttribute('class', 'card-header py-3')
        card_header_div_tag.appendChild(h6_tag)

        var card_shadow_div = document.createElement('div')
        card_shadow_div.setAttribute('class', 'cardliron shadow mb-4')

        card_shadow_div.appendChild(card_header_div_tag)
        card_shadow_div.appendChild(div_card_body)

        charts_node.appendChild(card_shadow_div)
        if (column == columns[0])
            return;

        var y1_axis = []
        for (i = 0; i < data.length; i++) {
            var curr_data = (data[i])[column]
            y1_axis.push(curr_data)
        }
        var myLineChart = null
        if (!should_plot_multiple_graphs) {
            myLineChart = new Chart(canvas_tag, {
                type: 'line',
                data: {
                    labels: frame_range,
                    datasets: [{
                        label: "Value ",
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(255, 255, 255, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                        pointHoverRadius: 3,
                        pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                        pointHitRadius: 10,
                        pointBorderWidth: 2,
                        data: y1_axis,
                    }],
                },
                options: {
                    bezierCurve: true,
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
        } else {
            var y2_axis = []
            for (i = 0; i < data.length; i++) {
                var curr_data = (data[i])[match_keypoint_column]
                y2_axis.push(curr_data)
            }
            columns.splice(columns.indexOf(match_keypoint_column), 1) // remove it because we don't want to plot this column again.
            myLineChart = new Chart(canvas_tag, {
                type: 'line',
                data: {
                    labels: frame_range,
                    datasets: [{
                        label: column,
                        lineTension: 0.3,
                        backgroundColor: "rgba(78, 115, 223, 0.05)",
                        borderColor: "rgba(78, 115, 223, 1)",
                        pointRadius: 3,
                        pointBackgroundColor: "rgba(255, 255, 255, 1)",
                        pointBorderColor: "rgba(78, 115, 223, 1)",
                        pointHoverRadius: 3,
                        pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                        pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                        pointHitRadius: 10,
                        pointBorderWidth: 2,
                        data: y1_axis,
                    },
                        {
                            label: match_keypoint_column,
                            lineTension: 0.3,
                            backgroundColor: "rgba(78, 115, 223, 0.05)",
                            borderColor: "rgba(255, 0, 0, 1)",
                            pointRadius: 3,
                            pointBackgroundColor: "rgba(255, 255, 255, 1)",
                            pointBorderColor: "rgba(255, 0, 0, 1)",
                            pointHoverRadius: 3,
                            pointHoverBackgroundColor: "rgba(255, 0, 0, 1)",
                            pointHoverBorderColor: "rgba(255, 0, 0, 1)",
                            pointHitRadius: 10,
                            pointBorderWidth: 2,
                            data: y2_axis,
                        }],
                },
                options: {
                    bezierCurve: true,
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
                        display: true
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

        }
        document.getElementById(canvas_id).onclick = function (evt) {
            var activePoints = myLineChart.getElementAtEvent(evt);
            // make sure click was on an actual point
            if (activePoints.length > 0) {
                var clickedDatasetIndex = activePoints[0]._datasetIndex;
                var clickedElementindex = activePoints[0]._index;
                var label = myLineChart.data.labels[clickedElementindex];
                var value = myLineChart.data.datasets[clickedDatasetIndex].data[clickedElementindex];
                console.log("dataset id : " + clickedDatasetIndex + " element index " + clickedElementindex + " Clicked: " + label + " - " + value)
                load_img(parseInt(label))
            }
        };
    })

}



function drawLine(id, xMin, xMax, yMin, yMax) {
    ctx.strokeStyle = "green";
    ctx.beginPath();
    ctx.lineWidth = "3"
    ctx.moveTo(xMin, yMin);
    ctx.lineTo(xMax, yMax);
    ctx.stroke();
}

function load_img(index) {
    current_img_path = '/static/temp/annotated_frames/annotated_frame_' + index + '.jpg'
    console.log(current_img_path)
    var c = document.getElementById("current frame to show");
    var ctx = c.getContext("2d");
    var drawLine = function (id, xMin, xMax, yMin, yMax) {
        ctx.strokeStyle = 'rgba(0, 255, 0,0.4)'
        ctx.beginPath();
        ctx.lineWidth = "10"
        ctx.moveTo(xMin, yMin);
        ctx.lineTo(xMax, yMax);
        ctx.stroke();
    };
    var image = new Image();

    image.onload = function (e) {
        ctx.canvas.width = image.width;
        ctx.canvas.height = image.height;
        c.width = image.width;
        c.height = image.height;
        ctx.drawImage(image, 0, 0);
        console.log("clicked");
    };
    image.style.display = "block";
    image.src = "/static/temp/annotated_frames/annotated_frame_" + index + ".jpg";

    var clicked = false;
    var fPoint = {};
    c.onclick = function (e) {
        console.log(clicked);
        if (!clicked) {
            var x = (image.width / c.scrollWidth) * e.offsetX;
            var y = (image.height / c.scrollHeight) * e.offsetY;
            console.log(e);
            ctx.strokeStyle = 'rgba(0, 255, 0,0.4)';
            ctx.fillStyle = 'rgba(0, 255, 0,0.4)';
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, 2 * Math.PI, false);
            ctx.fill();
            fPoint = {
                x: x,
                y: y
            };
        } else {
            var x2 = (image.width / c.scrollWidth) * e.offsetX;
            var y2 = (image.height / c.scrollHeight) * e.offsetY;

            drawLine(2, fPoint.x, x2, fPoint.y, y2)
            fPoint = {};
        }

        clicked = !clicked;
    };
}


function sendFixes() {
    var c = document.getElementById("current frame to show");
    var ctx = c.getContext("2d");
    var imgData = ctx.getImageData(0,0,ctx.canvas.width,ctx.canvas.height)
    console.log(current_img_path)
    imgData_url = c.toDataURL()
    var data = {'current url' : document.URL , 'img' : imgData_url , 'current img path' : current_img_path};
    // data = {'current_url' : document.URL , 'img' : 44}
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/_pass_data/',
        dataType: 'json',
        data: JSON.stringify(data),
        success: function (result) {
            console.log(2)
            console.log(result['returned_url'])
            jQuery("#clash").html(result['returned_url']);
        }, error: function (result) {
            console.log(3)
            console.log(result['returned_url']);
        }
    });
}

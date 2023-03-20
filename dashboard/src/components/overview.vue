<script lang="ts">
import * as d3 from "d3";
// import { sankey as d3Sankey, sankeyLinkHorizontal as d3SsankeyLinkHorizontal } from 'd3-sankey';
import axios from 'axios';
import { isEmpty, debounce, takeWhile } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

export default {
    data() {
        return {
            points: [] as ScatterPoint[],
            clusters: [] as string[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: {left: 50, right: 10, top: 10, bottom: 50} as Margin,
            coors: [] as string[],
            nodes: [],
            links: [],
            link_set: [],
            selected_ids: [],
            selected_sets: [],
            network_nodes: [],
            network_links: [],
            network_positions: [],
            network_notes: "",
            network_data: false,
            primitiveAdj: [],
            orig_graphlet_dist: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            orig_selected_count: 100,
            orig_select: -1,
            orig_hover: -1,
            orig_select_label: -1,
        }
    },
    computed: {
        rerender() {
            // return (!isEmpty(this.points))  && this.size
            return (!isEmpty(this.primitiveAdj))  && this.size
        },
    },
    created() {
        axios.get(`${server}/fetchPrimitive`)
            .then(resp => {
                this.primitiveAdj = resp.data.data;
                console.log(this.primitiveAdj);
                return true;
            })
            .catch(error => console.log(error));
    },
    methods: {
        onResize() {
            let target = this.$refs.overviewScatterContainer as HTMLElement
            if (target === undefined || target === null) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initLegend() {
            d3.select('#legend-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.legendContainer;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#legend-svg');

            chartContainer.append("circle")
                .attr("cx", this.margin.left)
                .attr("cy", this.margin.top + 10)
                .attr("r", 10)
                .attr('opacity', 0.8)
                .style("fill", "#da4f81");
            chartContainer.append("circle")
                .attr("cx", this.margin.left)
                .attr("cy", chart_size.height-this.margin.bottom-10)
                .attr("r", 10)
                .attr('opacity', 0.8)
                .style("fill", "#4D7AA7");
            
            chartContainer.append("text")
                .attr("x", this.margin.left + 20)
                .attr("y", this.margin.top + 10 +5)
                .style("fill", "#da4f81")
                .text("class 0: Question-Answering subreddit");
            chartContainer.append("text")
                .attr("x", this.margin.left + 20)
                .attr("y", chart_size.height-this.margin.bottom-10 +5)
                .style("fill", "#4D7AA7")
                .text("class 1: Discussion subreddit");
        },
        // 1-component PCA
        init_overview_scatterplot() {
            d3.select('#overviewScatter-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.overviewScatterContainer;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#overviewScatter-svg');

            const X = d3.map(this.primitiveAdj, d => d.pred[1]);
            const Y = d3.map(this.primitiveAdj, d => d.PCA1_graphlets_orig);
            const C = d3.map(this.primitiveAdj, d => d.label);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(chart_size.width / 80).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(chart_size.height / 80).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis)
                .call(g => g.append('text')
                    .attr('x', this.margin.left + (chart_size.width - this.margin.left - this.margin.right) / 2)
                    .attr('y', this.margin.bottom - 4)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'center')
                    .text("prediction probability"));
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 10)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlets distribution similarity"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr("label", i => C[i])
                .attr('fill', i => C[i] ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.5)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', 5)
                .on("click", click_graph)
                .on("mouseover", hover_graph)
                .on("mouseout", out_graph);

            function click_graph() {
                if (chartThis.orig_select == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 1)
                        .attr('r', 10);
                    chartThis.orig_select = parseInt(this.getAttribute('index'));
                    chartThis.orig_select_label = parseInt(this.getAttribute('label'));
                    chartThis.init_overview_graphlets();
                    chartThis.$emit('graphChange', chartThis.orig_select);
                    chartThis.$emit('graphColor', chartThis.orig_select_label);
                }
                else {
                    if (this.getAttribute('r') == 10) {
                        d3.select(this).transition()
                            .duration('50')
                            .attr('opacity', 0.5)
                            .attr('r', 5);
                        chartThis.orig_select = -1;
                        chartThis.$emit('graphChange', -1);
                    }
                    chartThis.init_overview_graphlets();
                }
            };

            function hover_graph() {
                if (chartThis.orig_select == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 1)
                        .attr('r', 10);
                    chartThis.orig_hover = parseInt(this.getAttribute('index'));
                    chartThis.orig_select_label = parseInt(this.getAttribute('label'));
                    chartThis.init_overview_graphlets();
                }
            };
            function out_graph() {
                if (chartThis.orig_select == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 0.5)
                        .attr('r', 5);
                    chartThis.orig_hover = -1;
                    chartThis.init_overview_graphlets();
                }
            };
        },
        init_overview_graphlets() {
            d3.select('#overviewGraphlet-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.overviewGraphletContainer;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#overviewGraphlet-svg');

            // calculated the selected graphs average graphlet distribution.

            if (this.orig_select == -1 && this.orig_hover == -1) {
                for (let i=0; i<21; i++) {
                    this.orig_graphlet_dist[i] = 0;
                }
                this.primitiveAdj.forEach(element => {
                    for (let i=0; i<21; i++) {
                        this.orig_graphlet_dist[i] += element.graphlets_orig[i];
                    }
                });
                for (let i=0; i<21; i++) {
                    this.orig_graphlet_dist[i] /= this.orig_selected_count;
                }
            }
            else if (this.orig_select != -1) {
                for (let i=0; i<21; i++) {
                    this.orig_graphlet_dist[i] = this.primitiveAdj[this.orig_select].graphlets_orig[i];
                }
            }
            else {
                for (let i=0; i<21; i++) {
                    this.orig_graphlet_dist[i] = this.primitiveAdj[this.orig_hover].graphlets_orig[i];
                }
            }
            
            // console.log(this.orig_graphlet_dist); // checked :)

            // graphlets_orig_average = []
            // for i in range(len(graphlets_orig[0])):
            //     graphlets_orig_average.append(np.sum(np.array(graphlets_orig)[:, i])/100)
            // print(graphlets_orig_average)

            const X = d3.map(this.orig_graphlet_dist, (d, i) => i + 1);
            const Y = d3.map(this.orig_graphlet_dist, d => d);
            const I = d3.range(Y.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.5, xDomain_tmp[1]+0.5];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(21);
            const yAxis = d3.axisLeft(yScale).ticks(chart_size.height / 80).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
                // .call(g => g.append('text')
                //     .attr('x', this.margin.left + (chart_size.width - this.margin.left - this.margin.right) / 2)
                //     .attr('y', this.margin.bottom - 4)
                //     .attr('fill', 'currentColor')
                //     .attr('text-anchor', 'center')
                //     .text("graphlet types"));
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 10)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text((this.orig_select==-1) ? ((this.orig_hover==-1) ? "average graphlet frequency" : "#"+this.orig_hover.toString()+" graphlet frequency") : "#"+this.orig_select.toString()+" graphlet frequency"));
            
            function draw_graphlet_dist(context) {
                for (let i=0; i<20; i++) {
                    context.moveTo(xScale(X[i]), yScale(Y[i]));
                    context.lineTo(xScale(X[i+1]), yScale(Y[i+1]));
                    
                }
                return context; // not mandatory, but will make it easier to chain operations
            };

            function draw_graphlets(id) {
                let graphlet_link_x, graphlet_link_y;
                if (id==1) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.8, 0.8, 1.2, 1.2, 1.3];
                    graphlet_link_y = [1.3, 1, 1, 0.7, 0.7, 0.7, 0.7, 1];
                }
                else if (id==2) {        
                    graphlet_link_x = [0.7, 1, 1, 1, 1, 0.7, 1, 1.3];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==3) {        
                    graphlet_link_x = [1, 0.7, 1, 0.7, 1, 1.3, 1, 1.3];
                    graphlet_link_y = [1, 0.7, 1, 1.3, 1, 0.7, 1, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==4) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.7, 1, 1.3, 1.3, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1, 1.3, 1.3, 0.7, 1, 1.3, 1.3, 0.7, 1.3, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==5) {        
                    graphlet_link_x = [0.7, 1, 1, 1, 1, 0.7, 1, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 0.7, 0.7, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==6) {        
                    graphlet_link_x = [1, 0.7, 1, 0.7, 1, 1.3, 1, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1, 0.7, 1, 1.3, 1, 0.7, 1, 1.3, 1.3, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==7) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.8, 0.8, 1.2, 1.2, 1.3, 1.3, 1];
                    graphlet_link_y = [1.3, 1, 1, 0.7, 0.7, 0.7, 0.7, 1, 1, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==8) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1, 1, 1.3, 1.3, 1];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 1.1, 1.1, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==9) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1, 1, 1.3, 1.3, 1, 1, 1];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 1.1, 1.1, 1.3, 1.3, 0.9];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==10) {        
                    graphlet_link_x = [1, 0.7, 1, 0.7, 1, 1.3, 1, 1.3, 0.7, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1, 0.7, 1, 1.3, 1, 0.7, 1, 1.3, 1.3, 1.3, 0.7, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==11) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1, 1, 1.3, 1.3, 1, 0.7, 1.3];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 1.1, 1.1, 1.3, 1.1, 1.1];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==12) {        
                    graphlet_link_x = [1.1, 0.7, 0.7, 0.7, 1.1, 1.3, 1.3, 1.3, 0.7, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1.1, 1.3, 1.3, 0.7, 1.1, 0.7, 1.3, 0.7, 1.3, 1.3, 0.7, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==13) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.7, 1, 1.3, 1.3, 1.3, 0.7, 1.3, 0.7, 1.3];
                    graphlet_link_y = [1, 1.3, 1.3, 0.7, 1, 1.3, 1.3, 0.7, 1.3, 1.3, 0.7, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==14) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1.3, 1.3, 1, 0.7, 1.3, 0.7, 1, 1.3, 1];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 1.1, 1.1, 1.3, 1.1, 1.1, 1.1, 0.7, 1.1, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==15) {        
                    graphlet_link_x = [0.7, 1, 1, 1, 1, 0.7, 1, 1.3, 0.7, 1.3, 1, 0.7, 1, 1.3];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 0.7, 0.9, 0.7, 0.7, 0.7, 1.1, 0.7, 1.1, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==16) {        
                    graphlet_link_x = [0.8, 0.8, 0.8, 0.8, 0.8, 1.2, 1.2, 1.2, 1.2, 0.8, 0.8, 1.2, 0.8, 1.2];
                    graphlet_link_y = [1.3, 1, 1, 0.7, 0.7, 0.9, 0.9, 1.1, 1.1, 1.3, 1, 1.1, 1, 0.9];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==17) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.7, 1, 1.3, 1.3, 1.3, 0.7, 1.3, 0.7, 1.3, 1, 0.7];
                    graphlet_link_y = [1, 1.3, 1.3, 0.7, 1, 1.3, 1.3, 0.7, 1.3, 1.3, 0.7, 0.7, 1, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==18) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1.3, 1.3, 1, 0.7, 1.3, 0.7, 1, 1.3, 1, 1, 1];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 1.1, 1.1, 1.3, 1.1, 1.1, 1.1, 0.7, 1.1, 0.7, 0.9, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==19) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.7, 1, 1.3, 1.3, 1.3, 0.7, 1.3, 0.7, 1.3, 1, 0.7, 1, 1.3];
                    graphlet_link_y = [1, 1.3, 1.3, 0.7, 1, 1.3, 1.3, 0.7, 1.3, 1.3, 0.7, 0.7, 1, 0.7, 1, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==20) {        
                    graphlet_link_x = [1, 0.7, 0.7, 1, 1, 1.3, 1.3, 1, 0.7, 1.3, 0.7, 1, 1.3, 1, 1, 1, 1, 1];
                    graphlet_link_y = [1.3, 1.1, 1.1, 0.9, 0.9, 1.1, 1.1, 1.3, 1.1, 1.1, 1.1, 0.7, 1.1, 0.7, 0.9, 0.7, 1.3, 0.9];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else if (id==21) {        
                    graphlet_link_x = [1, 0.7, 0.7, 0.8, 0.8, 1.2, 1.2, 1.3, 1.3,   1, 0.8,  1,  1.2,  1, 0.7, 1.3, 0.8, 1.3, 0.7, 1.2];
                    graphlet_link_y = [1.3, 1,   1, 0.7, 0.7, 0.7, 0.7,  1,    1, 1.3, 0.7, 1.3, 0.7, 1.3,  1,   1, 0.7,   1,   1, 0.7];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                else {
                    graphlet_link_x = [1, 0.7, 0.7, 0.8, 0.8, 1.2, 1.2, 1.3, 1.3, 1];
                    graphlet_link_y = [1.3, 1, 1, 0.7, 0.7, 0.7, 0.7, 1, 1, 1.3];
                    for (let i=0; i<graphlet_link_x.length; i++) {
                        graphlet_link_x[i] += id;
                        graphlet_link_x[i] -= 1;
                    }
                }
                return [graphlet_link_x, graphlet_link_y]; // not mandatory, but will make it easier to chain operations
            };

            // draw graphlet distribution line.
            chartContainer.append('path')
                .attr('stroke', (this.orig_hover == -1) ? "#339933": (this.orig_select_label ? "#4D7AA7" : "#da4f81"))
                .attr('stroke-width', 2)
                .attr('stroke-opacity', 0.6)
                .attr("d", draw_graphlet_dist(d3.path()));

            // draw overview graph data points.
            chartContainer.append('g')
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', 4)
                .attr('fill', (this.orig_hover == -1) ? "#339933" : (this.orig_select_label ? "#4D7AA7" : "#da4f81"))
                .attr('opacity', 0.6);
            
            // draw graphlet icons beside ticks.
            for (let i=1; i<=21; i++) {
                const tmp = draw_graphlets(i);
                const icon_x = tmp[0];
                const icon_y = tmp[1];
                let icon = [];
                for (let j=0; j<icon_x.length; j+=2) {
                    icon.push({
                        "x1": icon_x[j],
                        "x2": icon_x[j+1],
                        "y1": icon_y[j],
                        "y2": icon_y[j+1]
                    });
                }
                for (let j=0; j<icon.length; j++) {
                    chartContainer.append('g')
                        .attr('stroke', "#000000")
                        .attr('stroke-width', 1)
                        .attr('stroke-opacity', 1)
                        .selectAll('line')
                        .data(icon)
                        .join('line')
                        .attr('x1', d => xScale(d.x1))
                        .attr('x2', d => xScale(d.x2))
                        .attr('y1', d => chart_size.height+45-xScale(d.y1))
                        .attr('y2', d => chart_size.height+45-xScale(d.y2));
                }
            }

        },
        // use 2-compoenet PCA, but really hard to read.
        // init_overview_scatterplot_2d() { 
        //     const chartThis = this;

        //     let chartContainer = d3.select('#overviewScatter-svg');

        //     const X = d3.map(this.primitiveAdj, d => d.PCA21_graphlets_orig);
        //     const Y = d3.map(this.primitiveAdj, d => d.PCA22_graphlets_orig);
        //     const C = d3.map(this.primitiveAdj, d => d.label);
        //     const O = d3.map(this.primitiveAdj, d => d.pred)
        //     const I = d3.range(X.length);

        //     const xDomain_tmp = d3.extent(X);
        //     const yDomain_tmp = d3.extent(Y);

        //     const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
        //     const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

        //     const xRange = [this.margin.left, this.size.width - this.margin.right];
        //     const yRange = [this.size.height - this.margin.bottom, this.margin.top];

        //     const xScale = d3.scaleLinear(xDomain, xRange);
        //     const yScale = d3.scaleLinear(yDomain, yRange);

        //     const xAxis = d3.axisBottom(xScale).ticks(this.size.width / 80).tickSizeOuter(0);
        //     const yAxis = d3.axisLeft(yScale).ticks(this.size.height / 80).tickSizeOuter(0);

        //     const color = d3.schemeRdBu;

        //     // draw overview x axis.
        //     chartContainer.append('g')
        //         .attr('transform', `translate(0,${this.size.height - this.margin.bottom})`)
        //         .call(xAxis)
        //         .call(g => g.append('text')
        //             .attr('x', this.margin.left + (this.size.width - this.margin.left - this.margin.right) / 2)
        //             .attr('y', this.margin.bottom - 4)
        //             .attr('fill', 'currentColor')
        //             .attr('text-anchor', 'center')
        //             .text("graphlets distribution similarity component 1"));
            
        //     // draw overview y axis.
        //     chartContainer.append('g')
        //         .attr('transform', `translate(${this.margin.left},0)`)
        //         .call(yAxis)
        //         .call(g => g.append('text')
        //             .attr('transform', 'rotate(-90)')
        //             .attr('x', -this.size.height / 2)
        //             .attr('y', -this.margin.left + 10)
        //             .attr('fill', 'currentColor')
        //             .attr('text-anchor', 'middle')
        //             .text("graphlets distribution similarity component 2"));

        //     // draw overview graph data points.
        //     chartContainer.append('g')
        //         .selectAll('circle')
        //         .data(I)
        //         .join('circle')
        //         .attr('stroke', i => C[i] ? "#4D7AA7" : "#da4f81")
        //         .attr('stroke-width', 3)
        //         .attr('stroke-opacity', 0.7)
        //         .attr('fill', i => C[i] ? d3.interpolateRdBu(O[i][1]-0.01) : d3.interpolateRdBu(O[i][0]+0.01))
        //         .attr('cx', i => xScale(X[i]))
        //         .attr('cy', i => yScale(Y[i]))
        //         .attr('r', 5);

        // },
        // initChart_network() {
        //     const chartThis = this;
        //     this.selected_ids = [];
        //     this.selected_sets.forEach(element => {
        //         this.selected_ids.push(this.link_set[element]);
        //     });
        //     // console.log(this.selected_ids);

        //     axios.post(`${server}/fetchPrimitive`, {graph_id: [30, 91]})
        //         .then(resp => {
        //             this.primitiveAdj = resp.data.adj;
        //             console.log(this.primitiveAdj);
        //             return true;
        //         })
        //         .catch(error => console.log(error));

        //     axios.post(`${server}/fetchTwitch`, {set:this.selected_sets, id:this.selected_ids})
        //         .then(resp => {
        //             this.network_notes = resp.data.notes;
        //             this.network_nodes = resp.data.nodes;
        //             this.network_links = resp.data.links;
        //             this.network_positions = resp.data.positions;
        //             console.log(resp.data);
        //             this.network_data = true;
        //             this.drawChart_network();
        //             return true;
        //         })
        //         .catch(error => console.log(error));

        //     // while (!this.network_data) {
        //     // }
        //     // console.log("data is here");
        // },
        // drawChart_network() {
        //     d3.select('#network-svg').selectAll('*').remove()
        //     const chartThis = this;

        //     let chartContainer = d3.select('#network-svg')
        //     console.log(this.network_notes);

        //     // prepare network data
        //     const X = d3.map(this.network_positions, ([x]) => x);
        //     const Y = d3.map(this.network_positions, ([,y]) => y);
        //     const I = d3.range(X.length);
        //     const linkDraw = d3.map(this.network_links, ([s, t]) => [s, t]);
        //     const xDomain = d3.extent(X);
        //     const yDomain = d3.extent(Y);
        //     const xRange = [50, this.size.width - 50];
        //     const yRange = [this.size.height - 10, 10];
        //     const xScale = d3.scaleLinear(xDomain, xRange);
        //     const yScale = d3.scaleLinear(yDomain, yRange);
            
        //     // draw network links
        //     chartContainer.append('g')
        //         .attr('stroke', "#ccc")
        //         .attr('stroke-width', 0.7)
        //         .attr('stroke-opacity', 0.7)
        //         .selectAll('line')
        //         .data(linkDraw)
        //         .join('line')
        //         .attr('x1', link => xScale(X[link[0]]))
        //         .attr('x2', link => xScale(X[link[1]]))
        //         .attr('y1', link => yScale(Y[link[0]]))
        //         .attr('y2', link => yScale(Y[link[1]]));

        //     // draw network nodes
        //     chartContainer.append('g')
        //         .attr('stroke', "#ccc")
        //         .attr('stroke-width', 0.5)
        //         .selectAll('circle')
        //         .data(I)
        //         .join('circle')
        //         .attr('fill', "#99c")
        //         .attr('cx', i => xScale(X[i]))
        //         .attr('cy', i => yScale(Y[i]))
        //         .attr('r', 2);

        // },
        // initLegend() {
        //     let legendContainer = d3.select('#scatter-legend-svg')

        //     let clusterLabels: string[] = this.clusters.map((cluster: string, idx: number) => `Cultivar ${idx+1}`)
        //     let colorScale = d3.scaleOrdinal().domain(clusterLabels).range(d3.schemeTableau10)

        // }
    },
    watch: { // updated because a legend is added.
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                // d3.select('#scatter-svg').selectAll('*').remove()
                d3.select('#overviewScatter-svg').selectAll('*').remove();
                d3.select('#overviewGraphlet-svg').selectAll('*').remove();
                // d3.select('#scatter-legend-svg').selectAll('*').remove()
                this.initLegend();
                this.init_overview_scatterplot();
                this.init_overview_graphlets();
                // this.initChart_network()
                // this.initLegend()
            }
        },
    },
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100));
        this.onResize();
    },
    beforeDestroy() {
       window.removeEventListener('resize', this.onResize);
    }
}
</script>

<!-- We use flex to arrange the layout-->
<template>
    <div class="viz-container justify-end">
        <div class="legend-container" ref="legendContainer">
            <svg id="legend-svg" width="100%" height="100%"></svg>
        </div>
        <div class="chart-container" ref="overviewScatterContainer">
            <svg id="overviewScatter-svg" width="100%" height="100%"></svg>
        </div>
        <div class="dist-container" ref="overviewGraphletContainer">
            <svg id="overviewGraphlet-svg" width="100%" height="100%"></svg>
        </div>
        <!-- <div class="chart-title">
            <p >{{ network_notes }}</p>
        </div> -->
        <!-- <div class="chart-container d-flex" ref="networkContainer">
            <svg id="network-svg" width="100%" height="100%"></svg>
        </div> -->
    </div>
</template>

<!-- How we arrange the two svgs with css-->
<style scoped>
.viz-container{
    height:100%;
    width:100%;
    flex-direction: row;
    flex-wrap: nowrap;
}
/* .chart-title{
    width: 100%;
    height: 4%;
} */
.chart-container{
    /* width: calc(100% - 5rem); */
    width: 100%;
    height: 50%;
}
.dist-container{
    /* width: calc(100% - 5rem); */
    width: 100%;
    height: 30%;
}
.legend-container{
    /* width: calc(100% - 5rem); */
    width: 100%;
    height: 15%;
}
/* #overviewGraphlet-svg{
    width: 50%;
    height: 30%;
} */
</style>
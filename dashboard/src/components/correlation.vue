<script lang="ts">
import * as d3 from 'd3';
import * as d3Lasso from 'd3-lasso';
import axios from 'axios';
import { server } from '../helper';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin, Node, Link } from '../types';


export default {
    data() {
        return {
            nodes: [] as Node[],
            links: [] as Link[],
            selectedNodes: [] as Node[],
            graph_num: 0 as number,
            size: { width: 700, height: 700 } as ComponentSize, // size of graph
            margin: { left: 10, right: 10, top: 10, bottom: 10 } as Margin,
            forcedstrength: -10 as number,
            forcedgraphradius: 6 as number,
            graph_id_tmp: -1,
            instanceEmb: [],
            instanceGraphs: [],
            node_id_tmp: -1,        
        }
    },
    props: { // received data from others
        graphID: Number,
        graphColor: Number,
        nodeID: Number,
    },
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            if (this.graphID == -1) {
                return false && this.size;
            }
            if (this.nodeID != this.node_id_tmp) {
                console.log("node id change: ", this.nodeID);
                this.node_id_tmp = this.nodeID;
                if (this.instanceGraphs.includes(this.graphID)) {
                    this.init_corr1();
                    this.init_corr2();
                    this.init_corr3();
                    this.init_corr6();
                    this.init_corr8();
                    this.init_corr9();
                    this.init_corr12();
                }
                return this.size
            }
            if (this.graphID == this.graph_id_tmp) {
                return this.size;
            }
            this.graph_id_tmp = this.graphID;
            axios.post(`${server}/fetchExample`, { method: [this.graphID] })
                .then(resp => {
                    this.nodes = resp.data.nodes;
                    this.links = resp.data.edges;
                    return true;
                })
                .catch(error => console.log(error));
            return (!isEmpty(this.links)) && this.size
        },
    },
    created() { // Composition API syntax

        axios.get(`${server}/fetchInstance`)
            .then(resp => {
                this.instanceEmb = resp.data.data;
                console.log(this.instanceEmb);
                this.instanceGraphs = d3.map(this.instanceEmb, d => d.id);
                console.log(this.instanceGraphs);
                return true;
            })
            .catch(error => console.log(error));
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        init_corr1() {
            d3.select('#corr1-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_1;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr1-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][0];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet1 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr2() {
            d3.select('#corr2-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_2;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr2-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][1];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet2 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr3() {
            d3.select('#corr3-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_3;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr3-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][2];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet3 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr6() {
            d3.select('#corr6-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_6;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr6-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][5];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet6 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr8() {
            d3.select('#corr8-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_8;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr8-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][7];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet8 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr9() {
            d3.select('#corr9-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_9;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr9-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][8];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis);
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet9 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
        },
        init_corr12() {
            d3.select('#corr12-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.corrContainer_12;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#corr12-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA1_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.graphlets_node_orig)[emb_graph_idx][11];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = [0, 1];
            // const yDomain_tmp = d3.extent(Y);

            const xDomain = [xDomain_tmp[0]-0.05, xDomain_tmp[1]+0.05];
            const yDomain = [yDomain_tmp[0]-0.05, yDomain_tmp[1]+0.05];

            const xRange = [this.margin.left, chart_size.width - this.margin.right];
            const yRange = [chart_size.height - this.margin.bottom, this.margin.top];

            const xScale = d3.scaleLinear(xDomain, xRange);
            const yScale = d3.scaleLinear(yDomain, yRange);

            const xAxis = d3.axisBottom(xScale).ticks(0).tickSizeOuter(0);
            const yAxis = d3.axisLeft(yScale).ticks(0).tickSizeOuter(0);

            // draw overview x axis.
            chartContainer.append('g')
                .attr('transform', `translate(0,${chart_size.height - this.margin.bottom})`)
                .call(xAxis)
                .call(g => g.append('text')
                    .attr('x', this.margin.left + (chart_size.width - this.margin.left - this.margin.right) / 2)
                    .attr('y', this.margin.bottom)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'center')
                    .text("1D node embedding"));
            
            // draw overview y axis.
            chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left},0)`)
                .call(yAxis)
                .call(g => g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('x', -chart_size.height / 2)
                    .attr('y', -this.margin.left + 8)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'middle')
                    .text("graphlet12 freq"));

            // draw overview graph data points.
            chartContainer.append('g')
                .attr('stroke', "#ccc")
                .attr('stroke-width', 0.5)
                .selectAll('circle')
                .data(I)
                .join('circle')
                .attr('index', i => i)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.3)
                .attr('cx', i => xScale(X[i]))
                .attr('cy', i => yScale(Y[i]))
                .attr('r', i => (this.nodeID==-1) ? 5 : ((this.nodeID==i) ? 10 : 5));
            
            // chartContainer.append('g')
            //     .selectAll('text')
            //     .data(I)
            //     .join('text')
            //     .text(i => i)
            //     .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
            //     .attr('opacity', 0.8)
            //     .attr('x', i => xScale(X[i]))
            //     .attr('y', i => yScale(Y[i]));
        },
    },
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) { // Clean all the elements in the chart
                if (this.instanceGraphs.includes(this.graphID)) {
                    this.init_corr1();
                    this.init_corr2();
                    this.init_corr3();
                    this.init_corr6();
                    this.init_corr8();
                    this.init_corr9();
                    this.init_corr12();
                }
            }
        },
    },
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.onResize)
    }
};
</script>

<template>
    <div class="viz-container d-flex">
        <div class="chart-container" ref="corrContainer_1">
            <svg id="corr1-svg" width="100%" height="100%"></svg>
        </div>
        <div class="chart-container" ref="corrContainer_2">
            <svg id="corr2-svg" width="100%" height="100%" ></svg>
        </div>
        <div class="chart-container" ref="corrContainer_3">
            <svg id="corr3-svg" width="100%" height="100%" ></svg>
        </div>
        <div class="chart-container" ref="corrContainer_6">
            <svg id="corr6-svg" width="100%" height="100%"></svg>
        </div>
        <div class="chart-container" ref="corrContainer_8">
            <svg id="corr8-svg" width="100%" height="100%" ></svg>
        </div>
        <div class="chart-container" ref="corrContainer_9">
            <svg id="corr9-svg" width="100%" height="100%" ></svg>
        </div>
        <div class="chart-container" ref="corrContainer_12">
            <svg id="corr12-svg" width="100%" height="100%"></svg>
        </div>
    </div>
</template>

<style scoped>
.viz-container {
    height: 100%;
    width: 100%;
    flex-direction: column;
    flex-wrap: wrap;
}

.chart-container {
    width: 50%;
    height: 13%
}

</style>
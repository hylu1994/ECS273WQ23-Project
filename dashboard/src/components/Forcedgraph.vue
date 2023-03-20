<script lang="ts">
import * as d3 from 'd3';
import * as d3Lasso from 'd3-lasso';
import axios from 'axios';
import { server } from '../helper';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin, Node, Link } from '../types';
// D3 verison: 5.16.0
// Todo: 
//       when selecting specific graph, it may take some time for data to be fetched, so the graph may be staying in the previous graph
//       add margin for the graph canvas
//       add select specific nodes
//       add input check
//       add interaction to select gravity force
//       html beautify
//       code reconfiguration

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
            forcedgraphradius: 15 as number,
            graph_id_tmp: -1,
            instanceEmb: [],
            instanceGraphs: [],
            node_selected_id: -1,
            nodeSelected: false,
            node_hover_id: -1,
        }
    },
    props: { // received data from others
        graphID: Number,
        graphColor: Number
    },
    computed: {
        // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
        rerender() {
            if (this.graphID == -1) {
                return false && this.size;
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
            
            axios.get(`${server}/fetchInstance`)
                .then(resp => {
                    this.instanceEmb = resp.data.data;
                    console.log(this.instanceEmb);
                    this.instanceGraphs = d3.map(this.instanceEmb, d => d.id);
                    console.log(this.instanceGraphs);
                    return true;
                })
                .catch(error => console.log(error));
            return (!isEmpty(this.links)) && this.size
        },
    },
    created() { // Composition API syntax
        // // Get data from backend
        // axios.post(`${server}/fetchExample`, { method: [38] })
        //     .then(resp => {
        //         this.nodes = resp.data.nodes;
        //         this.links = resp.data.edges;
        //         return true;
        //     })
        //     .catch(error => console.log(error));

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
        buttonClick() {
            // // Get data from backend
            // axios.post(`${server}/fetchExample`, { method: this.graph_num.toString() })
            //     .then(resp => {
            //         this.nodes = resp.data.nodes;
            //         this.links = resp.data.edges;
            //         return true;
            //     })
            //     .catch(error => console.log(error));
            // get data from backend end
            console.log('Input is ' + this.graph_num);
            d3.select(this.$refs.canvas).selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        },
        initChart() {
            console.log(this.graphID);

            const chartThis = this;

            // // Get data from backend
            // axios.post(`${server}/fetchExample`, { method: [this.graphID] })
            //     .then(resp => {
            //         this.nodes = resp.data.nodes;
            //         this.links = resp.data.edges;
            //         console.log([this.graphID]);
            //         return true;
            //     })
            //     .catch(error => console.log(error));
            // console.log(d3);
            let target = this.$refs.canvasContainer;
            const width = target.clientWidth;
            const height = target.clientHeight;
            const nodes = this.nodes;
            const links = this.links;

            let chartContainer = d3.select('#canvas-svg');

            const simulation = d3
                .forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id))
                .force('charge', d3.forceManyBody().strength(this.forcedstrength)) // Forced strength
                .force('collide', d3.forceCollide().radius(this.forcedgraphradius))
                .force('center', d3.forceCenter((width-this.margin.left-this.margin.right)/2, (height-this.margin.top-this.margin.bottom)/2)); // Forced center

            const g = chartContainer.append('g').attr('class', 'everything');

            const link = g
                .selectAll('line')
                .data(links)
                .join('line')
                .attr('stroke', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('stroke-opacity', 0.3)
                .attr('stroke-width', 1.3); // Link width

            const node = g.selectAll('circle')
                .data(nodes)
                .join('g');

            node.append('circle')
                .attr('index', d => d.id)
                .attr('r', 3)
                .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
                .attr('opacity', 0.8)
                .on("click", click_node)
                .on("mouseover", hover_node)
                .on("mouseout", out_node)
                .call(drag(simulation)); // Drag function

            // node.append('text')
            //     .text(d => d.id)
            //     .attr('fill', this.graphColor ? "#4D7AA7" : "#da4f81")
            //     .attr('opacity', 0.8)
            //     .attr('x', 2)
            //     .attr('y', 2);
            
            function click_node() {
                if (chartThis.node_selected_id == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 1)
                        .attr('r', 8);
                    chartThis.node_selected_id = parseInt(this.getAttribute('index'));
                    chartThis.init_embedding_scatterplot();
                    chartThis.$emit('nodeChange', chartThis.node_selected_id);
                }
                else {
                    if (this.getAttribute('r') == 8) {
                        d3.select(this).transition()
                            .duration('50')
                            .attr('opacity', 0.8)
                            .attr('r', 3);
                        chartThis.node_selected_id = -1;
                        chartThis.$emit('nodeChange', chartThis.node_selected_id);
                    }
                    chartThis.init_embedding_scatterplot();
                }
            };

            function hover_node() {
                if (chartThis.node_selected_id == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 1)
                        .attr('r', 8);
                    chartThis.node_hover_id = parseInt(this.getAttribute('index'));
                    chartThis.$emit('nodeChange', chartThis.node_hover_id);
                    chartThis.init_embedding_scatterplot();
                }
            };
            function out_node() {
                if (chartThis.node_selected_id == -1) {
                    d3.select(this).transition()
                        .duration('50')
                        .attr('opacity', 0.8)
                        .attr('r', 3);
                    chartThis.node_hover_id = -1;
                    chartThis.$emit('nodeChange', chartThis.node_hover_id);
                    chartThis.init_embedding_scatterplot();
                }
            };

            // Lasso functions
            var lasso_start = function () {
                lasso.items()
                    .attr("r", 3.5) // reset size
                    .classed("not_possible", true)
                    .classed("selected", false);
            };

            var lasso_draw = function () {

                // Style the possible dots
                lasso.possibleItems()
                    .classed("not_possible", false)
                    .classed("possible", true);

                // Style the not possible dot
                lasso.notPossibleItems()
                    .classed("not_possible", true)
                    .classed("possible", false);
            };

            var lasso_end = function () {
                // Reset the color of all dots
                lasso.items()
                    .classed("not_possible", false)
                    .classed("possible", false);

                // Style the selected dots
                lasso.selectedItems()
                    .classed("selected", true)
                    .attr("r", 7);

                // Reset the style of the not selected dots
                lasso.notSelectedItems()
                    .attr("r", 3.5);

            };
            // // BUGS
            // var lasso = d3Lasso.lasso()
            //     .closePathSelect(true)
            //     .closePathDistance(100)
            //     .items(g.selectAll("circle"))
            //     .targetArea(g.selectAll("circle"))
            //     .on("start", lasso_start)
            //     .on("draw", lasso_draw)
            //     .on("end", lasso_end);
            // lasso(svg);

            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                node.attr('transform', d => `translate(${d.x},${d.y})`);
            });

            // Zoom functions
            const zoomHandler = d3.zoom().on('zoom', zoomActions);
            zoomHandler(chartContainer)
            function zoomActions() {
                g.attr('transform', d3.event.transform)
            }

            // drag functions
            function drag(simulation) {
                function dragstarted(d) {
                    if (!d3.event.active) simulation.alphaTarget(0.1).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }

                function dragged(d) {
                    d.fx = d3.event.x;
                    d.fy = d3.event.y;
                }

                function dragended(d) {
                    if (!d3.event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }

                return d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended);
            }
        },
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        init_embedding_scatterplot() {
            d3.select('#embedding-svg').selectAll('*').remove();
            const chartThis = this;
            let target = this.$refs.embeddingContainer;
            const chart_size = { width: target.clientWidth, height: target.clientHeight };

            let chartContainer = d3.select('#embedding-svg');

            const emb_graph_idx = this.instanceGraphs.indexOf(this.graphID);
            const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb)[emb_graph_idx];
            const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb)[emb_graph_idx];
            // console.log(emb_graphs_x, emb_graphs_y);
            // const X = d3.map(this.instanceEmb, d => d.PCA21_node_emb[emb_graph_idx]);
            // const Y = d3.map(this.instanceEmb, d => d.PCA22_node_emb[emb_graph_idx]);
            // console.log(this.graphID);
            // console.log(X);
            const I = d3.range(X.length);

            const xDomain_tmp = d3.extent(X);
            const yDomain_tmp = d3.extent(Y);

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
                    .attr('y', this.margin.bottom-3)
                    .attr('fill', 'currentColor')
                    .attr('text-anchor', 'center')
                    .text("PCA component=2 node embedding layout"));

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
                .attr('r', i => (this.node_selected_id==-1) ? ((this.node_hover_id==-1) ? 5 : ((this.node_hover_id==i) ? 10 : 5)) : ((this.node_selected_id==i) ? 10 : 5));
            
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
            if (!isEmpty(newSize)) {
                d3.select('#canvas-svg').selectAll('*').remove(); // Clean all the elements in the chart
                this.initChart();
                if (this.instanceGraphs.includes(this.graphID)) {
                    this.init_embedding_scatterplot();
                }
            }
        },
        // graphID(newVal, oldVal) { // watch it
        //     console.log("notice from parent graph id changed: ", newVal);

        //     // Get data from backend
        //     axios.post(`${server}/fetchExample`, { method: [newVal] })
        //         .then(resp => {
        //             this.nodes = resp.data.nodes;
        //             this.links = resp.data.edges;
        //             return true;
        //         })
        //         .catch(error => console.log(error));
            
        //     this.initChart();
        // },
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
    <div class="viz-container ">
        <div class="chart-container" ref="canvasContainer">
            <svg id="canvas-svg" width="100%" height="100%"></svg>
        </div>
        <div class="emb-container" ref="embeddingContainer">
            <svg id="embedding-svg" width="100%" height="100%" ></svg>
        </div>
        <!-- <div id=" chart-control-container">
            <label :style="{ fontSize: '0.7rem' }"> Type graph number[0-1999]:</label><br>
            <input placeholder="HERE" v-model="graph_num" class="inputbox" /><br>
            <button @click="buttonClick" class="button">Jump to</button><br>
            <button @click="buttonClick" class="button">Center</button>
            <button class="button">Lasso select</button>
        </div> -->
    </div>
</template>

<style scoped>
.viz-container {
    height: 100%;
    width: 100%;
    flex-direction: row;
    flex-wrap: nowrap;
}

.chart-container {
    height: 60%;
    width: 100%;
    /* border-width: 2px;
    border-color: #c60d0d; */
}
.emb-container {
    height: 30%;
    width: 100%;
    align-items: center;
    justify-content: center;
    /* border-width: 2px;
    border-color: #c60d0d; */
}

#chart-control-container {
    width: 10rem;
    flex-direction: column;
}

.inputbox {
    width: 80px;
    border: 1px solid black;
    border-radius: 4px;
}

.button {
    width: 100px;
    border: 5cap;
    color: rgb(0, 0, 0);
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 12px;
    margin: 2px 1px;
    cursor: pointer;
    background-color: #8c8c8c;
    border-radius: 6px;
}

.selected {
    fill: red;
}
</style>
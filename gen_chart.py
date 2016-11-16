import argparse
import bisect
from collections import defaultdict
import datetime
from math import pi

import bokeh.plotting as bokeh_plotting  # import figure, output_file, show, ColumnDataSource
import bokeh.models as bokeh_models  # import HoverTool, DatetimeTickFormatter


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interval", default=5, type=int, help="time intervals in minutes; defaults to 5 minutes")
required = parser.add_argument_group('Required')
required.add_argument("-f", "--file", type=str, required=True, help="datafile")
required.add_argument("-s", "--start", type=str, required=True, help="start date; YYYY-mm-dd")
required.add_argument("-e", "--end", type=str, required=True, help="end date; YYYY-mm-dd")


class Data(object):

    def __init__(self, data_file, start_date, end_date, interval):
        self.data_file = data_file
        self.start_time = datetime.datetime.strptime('{} 06:00:00'.format(start_date), '%Y-%m-%d %H:%M:%S')
        self.end_time = datetime.datetime.strptime('{} 06:00:00'.format(end_date), '%Y-%m-%d %H:%M:%S')
        self.interval = interval or 5

    @property
    def log_entries(self):
        logs = []
        with open('{}'.format(self.data_file), 'r') as f:
            for line in f:
                logs.append(line)  # .split('|')[1].strip())
        return logs

    @property
    def time_slots(self):
        time_slots = [str(self.start_time)]
        next_time = self.start_time + datetime.timedelta(minutes=self.interval)
        while next_time < self.end_time:
            time_slots.append(str(next_time))
            next_time = next_time + datetime.timedelta(minutes=self.interval)
        return time_slots

    def group_log_entries(self):
        groups = defaultdict(lambda: defaultdict(list))
        slots = self.time_slots
        for slot in slots:
            groups[slot]['time'] = slot
        for log in self.log_entries:
            idx = bisect.bisect_left(slots, log)
            groups[slots[idx - 1]]['logs'].append(log)
        return groups

    def add_stats_to_groups(self, groups):
        for group in groups:
            groups[group]['count'] = len(groups[group]['logs'])
            groups[group]['avg_per_min'] = groups[group]['count'] / 5
            groups[group]['avg_per_second'] = groups[group]['count'] / (5 * 60)
        return groups

    def get_data(self):
        groups = self.group_log_entries()
        data = self.add_stats_to_groups(groups)
        points = []
        for key in sorted(groups.keys()):
            amount = groups[key]['count']
            date = (datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=6))
            points.append({
                'x': date,
                'y': amount,
                'time': '{}'.format(date),
                'count': amount,
                'avg_per_min': groups[key]['avg_per_min'],
                'avg_per_sec': groups[key]['avg_per_second'],
            })
        return points

    def print_data(self, data):
        print('TOTALS: Files Processed: {}'.format(len(logs)))
        print('{:^19}    {:^5}    {:^7}    {:^7}'.format('Time', 'Count', 'Avg/min', 'Avg/sec'))
        for datum in data:
            print('{}    {:>5}    {:>7}    {:>7.3f}'.format(
                datum['time'],
                datum['count'],
                datum['avg_per_min'],
                datum['avg_per_second'],
            ))


class Graph(object):

    def __init__(self, data, interval=5, out_file='graph.html'):
        self.data = data
        self.interval = interval
        self.chart = self.create_chart()
        bokeh_plotting.output_file(out_file)

    @property
    def source(self):
        return bokeh_plotting.ColumnDataSource(
            data=dict(
                x=[datum['x'] for datum in self.data],
                y=[datum['y'] for datum in self.data],
                time=[datum['time'] for datum in self.data],
                count=[datum['count'] for datum in self.data],
            )
        )

    @property
    def hover(self):
        return bokeh_models.HoverTool(
            names=['points'],
            tooltips=[
                ('Time', '@time'),
                ('Count', '@count'),
            ]
        )

    def create_plot(self):
        plot = bokeh_plotting.figure(
            width=1000,
            height=500,
            title='Files per {} minutes'.format(self.interval),
            x_axis_label='Time (UTC)',
            x_axis_type='datetime',
            y_axis_label='Fileprocesslog Count',
        )
        plot.add_tools(self.hover)
        plot.xaxis.formatter=bokeh_models.DatetimeTickFormatter(
                minutes=["%H:%M"],
                hours=["%H:%M"],
                days=["%Y-%m-%d"],
        )
        plot.xaxis.major_label_orientation = pi/4
        return plot

    def create_line_graph(self, plot):
        plot.line(
            'x',
            'y',
            source=self.source,
            line_width=1,
            color='gray'
        )
        return plot

    def create_circle_graph(self, plot):
        plot.circle(
            'x',
            'y',
            name='points',
            source=self.source,
            line_color='olive',
            legend='Files Processed'
        )
        return plot

    def create_chart(self):
        plot = self.create_plot()
        plot = self.create_line_graph(plot)
        plot = self.create_circle_graph(plot)
        return plot

    def output_chart(self):
        bokeh_plotting.show(self.chart)


if __name__ == '__main__':
    args = parser.parse_args()
    data = Data(args.file, args.start, args.end, args.interval).get_data()
    chart = Graph(data, interval=args.interval)
    chart.output_chart()

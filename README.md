Creates a graph using the Bokeh library. 

Uses a log of timestamps grouped into buckets set by the `interval` passed to the program.

### Install

Install dependencies `pip install -r requirements.txt`

### To Run
Example:

`python3 gen_chart.py -f 11-15 -s 2016-11-15 -e 2016-11-16 -i 10`

`python3 gen_chart.py --file 11-16 --start 2016-11-16 --end 2016-11-17`
    
    usage: gen_chart.py [-h] [-i INTERVAL] -f FILE -s START -e END

    optional arguments:
       -h, --help            show this help message and exit
       -i INTERVAL, --interval INTERVAL
                        time intervals in minutes; defaults to 5 minutes

    Required:
     -f FILE, --file FILE  datafile
     -s START, --start START  start date; YYYY-mm-dd
     -e END, --end END          end date; YYYY-mm-dd
     

### Output

Outputs an html file with the chart (default named 'graph.html')

### Reference
http://bokeh.pydata.org/en/latest/
     
     
### TODO
- [ ] Don't hardcode timezones
- [ ] Default endtime to one day from passed in start so you don't have to pass in
- [ ] Start datetime + offset?  ex: (2016-11-01 14:00 for 3 hours)

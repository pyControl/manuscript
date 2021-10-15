'''
Analysis code for pyControl manuscript vaidation experiments.
'''

import os
import numpy as np 
import pylab as plt

from scipy.io import loadmat

import data_import as di

# Plotting parameters.
plt.rcParams['pdf.fonttype'] = 42
plt.rc("axes.spines", top=False, right=False)

# -----------------------------------------------------------------------------
# Generate figure
# -----------------------------------------------------------------------------

def generate_figure():
    latency_analysis('low_load.mat' , fig_no=1 , title='low load')
    latency_analysis('high_load.mat', fig_no=2 , title='high load')
    timing_accuracy('low_load_10ms_pulses.mat' , fig_no=3, title='low load')
    timing_accuracy('high_load_10ms_pulses.mat', fig_no=4, title='high load')
    gc_timer_analysis(fig_no=5)
    gc_inputs_analysis(fig_no=6)

# -----------------------------------------------------------------------------
# Latency analysis
# -----------------------------------------------------------------------------

def latency_analysis(file_name, fig_no=1, title=''):
    '''Plot the distribution over all rising and falling edges of the
    latency between an input and output signals.'''

    # Import data.

    data_path = os.path.join('..', 'data', 'response latency', file_name)
    data = loadmat(data_path)

    # Calculate latencies.

    input_rising , input_falling  = get_edge_times(data, 'B')
    output_rising, output_falling = get_edge_times(data, 'A')
    input_rising , input_falling  = complete_pulses(input_rising, input_falling)
    output_rising, output_falling = complete_pulses(output_rising, output_falling)
    input_rising , input_falling, output_rising, output_falling = input_leads(
        input_rising , input_falling, output_rising, output_falling) 

    rising_latencies  = output_rising  - input_rising
    falling_latencies = output_falling - input_falling

    all_latencies = np.hstack([rising_latencies, falling_latencies])

    # Plotting

    plt.figure(fig_no, clear=True, figsize=[3,3])
    bins = np.arange(np.min(all_latencies)-50, np.max(all_latencies)+50, 20)
    plt.hist(all_latencies , bins)
    plt.ylabel('# events')
    plt.xlabel('Latency (μs)')
    plt.title('Response latency ' + title)
    plt.tight_layout()

    print(f'Latency mean:{np.mean(all_latencies):.0f}, SD:{np.std(all_latencies):.0f}, '
          f'min:{np.min(all_latencies):.0f}, max:{np.max(all_latencies):.0f}')
    print(f'Fraction of edge latencies < 2ms: {np.mean(all_latencies<2000) :.4f}')

# -----------------------------------------------------------------------------
# Output timing accuracy
# -----------------------------------------------------------------------------

def timing_accuracy(file_name, target_dur_ms=10, fig_no=1, title=''):
    '''Plot the distribution of discrepancies between the duration
    of high pulses in the signal and the target duration.'''

    # Import data.

    data_path = os.path.join('..', 'data', 'timing accuracy', file_name)
    data = loadmat(data_path)
   
    # Calculate pulse durations.

    rising_edges, falling_edges  = get_edge_times(data, 'A')
    rising_edges, falling_edges = complete_pulses(rising_edges, falling_edges)
    
    pulse_durs = falling_edges - rising_edges
    dur_errors = pulse_durs-target_dur_ms*1000
     
    # Plotting

    plt.figure(fig_no, clear=True, figsize=[3,3])
    bins = np.arange(np.min(dur_errors)-50, np.max(dur_errors)+50, 20)
    plt.hist(dur_errors, bins)
    plt.ylabel('# events')
    plt.xlabel('Timing error (μs)')
    plt.title('Timing accuracy ' + title)
    plt.tight_layout()

    print(f'Error mean:{np.mean(dur_errors):.0f}, SD:{np.std(dur_errors):.0f}, '
          f'min:{np.min(dur_errors):.0f}, max:{np.max(dur_errors):.0f}')
    print(f'Fraction of errors < 1ms: {np.mean(dur_errors<1000) :.4f}')


# -----------------------------------------------------------------------------
# Maximum event rate analysis
# -----------------------------------------------------------------------------

def missed_event_analysis(fig_no=1):
    '''For a set of data files each comprising an output signal following
    an input square wave at different frequencies, compute the fraction 
    of input edges that are missed in the output signal an plot as a 
    function of frequency.'''

    data_dir = os.path.join('..', 'data', 'maximum event rate')
    file_names = os.listdir(data_dir)
    file_event_rates = [int(file_name.split('Hz')[0])*2 for file_name in file_names]
    file_missed_proportions = [_missed_proportion(os.path.join(data_dir, file_name))
                               for file_name in file_names]
    plt.figure(fig_no, figsize=[3,3], clear=True)
    plt.plot(file_event_rates, np.array(file_missed_proportions)*100, 'o')
    plt.xlabel('Continuous event rate (Hz)')
    plt.ylabel('Proportion of missed events (%)')
    plt.axhline(0, 0, color='k', linewidth=0.5)
    plt.xlim(0, 1000)
    plt.ylim(-0.5, 6)
    plt.tight_layout()


def _missed_proportion(data_path):
    '''Compute the proportion of events missed for one data file.'''

    # Import data.

    data = loadmat(data_path)

    # Find rising and falling edges.

    input_rising , input_falling  = get_edge_times(data, 'B')
    output_rising, output_falling = get_edge_times(data, 'A')
    input_rising , input_falling  = complete_pulses(input_rising, input_falling)
    output_rising, output_falling = complete_pulses(output_rising, output_falling)
    input_rising , input_falling, output_rising, output_falling = input_leads(
        input_rising , input_falling, output_rising, output_falling)

    # Proportion of events missed.

    n_input_events  = len(input_rising) + len (input_falling)
    n_output_events = len(output_rising) + len (output_falling)
    p_missed = (n_input_events-n_output_events)/n_input_events
    return p_missed

# -----------------------------------------------------------------------------
# Garbage collection effects analysis
# -----------------------------------------------------------------------------

def high_frequency_timer_analysis(fig_no=1):
    '''Analysis looking at the effects of garbage collection. Data is 
    generated by a task that toggles between two states with output on 
    and off every 1ms using pyControl timers.  The output signal is
    recorded and garbage collection can be seen by occasional longer 
    intervals between edges in the signal.  This function evaluates
    the fraction of edges where garbage collection occured, the average
    duration of these delayed intervals, and plots the signal over 200ms.
    '''
    data_dir = os.path.join('..', 'data', 'garbage collection')
    data_path = os.path.join(data_dir, '1ms_squre_wave.mat')
    data = loadmat(data_path)
    rising_edges, falling_edges = get_edge_times(data, 'A')
    rising_edges, falling_edges = complete_pulses(rising_edges, falling_edges)
    all_edges = np.reshape(np.stack([rising_edges, falling_edges]).T,
                             (1,-1)).squeeze()
    IEIs = np.diff(all_edges)
    print(f'Fraction of inter edge intervals > 1.1ms: {np.mean(IEIs>1100):.4f}')
    print(f'Mean duration of intervals > 1.1ms: {int(np.mean(IEIs[IEIs>1100]))}us')
    # plotting.
    si_ms = data['Tinterval'].squeeze()*1e3 # Sampling interval in ms
    plt.figure(fig_no, figsize=[3,3], clear=True)
    plt.plot(np.arange(10000)*si_ms, data['A'][:10000])
    plt.xlabel('Time (ms)')
    plt.ylabel('Signal (V)')
    plt.xlim(0,200)
    plt.tight_layout()

def gc_timer_analysis(fig_no=1):
    '''Demonstration of how garbage collection affects pyControl timers.
    Plots two traces showing square waves generated by two timers, one 
    with 1ms intervals and one with 5ms intervals, around the time
    when a garbage collection has occured.  The 1ms timer which 
    elapsed during the garbage collection is only processed once it has 
    finished.  The 5ms timer which does not elapse during garbage
    collection is unaffected.
    '''
    data_dir = os.path.join('..', 'data', 'garbage collection')
    data_path = os.path.join(data_dir, 'garbage_collection_timer_example.mat')
    data = loadmat(data_path)
    si_ms = data['Tinterval'].squeeze()*1e3 # Sampling interval in ms
    plt.figure(fig_no, figsize=[3,3], clear=True)
    plt.plot(np.arange(1500)*si_ms, data['A'][55000:56500]+4)
    plt.plot(np.arange(1500)*si_ms, data['B'][55000:56500])
    plt.xlabel('Time (ms)')
    plt.ylabel('Signal (V)')
    plt.xlim(0,25)
    plt.title('Garbage collection\neffect on timers')
    plt.tight_layout()

def gc_inputs_analysis(fig_no=1):
    '''Demonstration of how garbage collection affects pyControl inputs.
    An input waveform consisting of 1ms pulses every 10ms is provided to
    3 pyControl digital inputs, one of which records only rising events,
    one only falling events, and one both rising and falling events. A
    timer triggers garbage collection 1ms before a subset of the pulses
    such that rising and falling events occur during garbage collection.
    This does not affect the inputs which record a single edge but causes
    the input which records both edges to miss an edge.
    '''
    data_dir = os.path.join('..', 'data', 'garbage collection')
    event_data = di.Session(os.path.join(data_dir, 'gc_input_test.txt'))
    plt.figure(fig_no, figsize=[4.5,3], clear=True)
    plt.plot(event_data.times['rising_1'  ], 1+np.zeros(event_data.times['rising_1'  ].shape), '|', markersize=10, label='In3 rising')
    plt.plot(event_data.times['falling_1' ], 1+np.zeros(event_data.times['falling_1' ].shape), '|', markersize=10, label='In3 falling')
    plt.plot(event_data.times['rising_2'  ], 3+np.zeros(event_data.times['rising_2'  ].shape), '|', markersize=10, label='In1 rising')
    plt.plot(event_data.times['falling_3' ], 2+np.zeros(event_data.times['falling_3' ].shape), '|', markersize=10, label='In2 falling')
    plt.plot(event_data.times['trigger_gc'], 4+np.zeros(event_data.times['trigger_gc'].shape), '^', label='trigger GC')
    plt.ylim(0.5,4.5)
    plt.xlim(95,170)
    plt.xlabel('Time ms')
    plt.ylabel('Input #')
    plt.legend(bbox_to_anchor=(1, 0.5))
    plt.title('Garbage collection\neffect on inputs')
    plt.tight_layout()

# -----------------------------------------------------------------------------
# Simultaneous inputs
# -----------------------------------------------------------------------------

def simultaneous_inputs_analysis():
    '''Test whether edges recieved simultaneously at 5 different 
    digital inputs always generate framework events.  The edges are 
    generated by the same task that is recording the events and occur
    at transitions between output_on and output_off states.  To assess
    whether all events are recorded as expected, evalutes the number
    of unique combinations of pyControl events generated during each
    output_on and output_off state.  If all events are recorded on 
    all transitions then this should be only a single set of events
    for each of the two states.
    '''
    data_dir = os.path.join('..', 'data', 'simultaneous_inputs')
    file_name = 'simultaneous_inputs_data.txt'
    data = di.Session(os.path.join(data_dir, file_name))
    on_events = []   # List to store sets of events generated by on transitions.
    off_events = []  # List to store sets of events generated by off transitions.
    current_set = []
    for ev in data.events[2:]:
        if ev.name == 'output_on':
            off_events.append(tuple(current_set))
            current_set = []
        elif ev.name == 'output_off':
            on_events.append(tuple(current_set))
            current_set = []
        else:
            current_set.append(ev.name)
    unique_on_events  = set(on_events)
    unique_off_events = set(off_events)
    if len(unique_on_events) == 1 and len(unique_off_events) == 1:
        print('All events recorded for all edges.')
    else:
        print('Not all events recorded as expected.')
        print(unique_on_events)
        print(unique_off_events)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def get_edge_times(data, channel):
    '''Return the times in us of rising and falling edges on the 
    specified channel'''
    sampling_interval_us = data['Tinterval'].squeeze()*1e6
    signal  = (data[channel].squeeze()>1).astype(int) # Signal converted to int 0/1  for low high.
    rising_edges  = np.where(np.diff(signal)== 1)[0]*sampling_interval_us
    falling_edges = np.where(np.diff(signal)==-1)[0]*sampling_interval_us
    return rising_edges, falling_edges

def complete_pulses(rising_edges, falling_edges):
    '''Ensure first edge is rising and there are the same number of rising
    and falling edges.'''
    if rising_edges[0] > falling_edges[0]:
        falling_edges = falling_edges[1:] # Ensure first edge is rising.
    if len(rising_edges) > len(falling_edges):
        rising_edges = rising_edges[:len(falling_edges)] # Ensure same number of rising and falling edges.
    return rising_edges, falling_edges

def input_leads(input_rising , input_falling, output_rising, output_falling):
    '''Ensure the first input pulse occurs before the first output
    pulse and last output pulse follows last input pulse.'''
    if input_rising[0] > output_rising[0]:   # Ensure first pulse is input.
        output_rising  = output_rising[1:]
        output_falling = output_falling[1:]
    if input_rising[-1] > output_rising[-1]: # Ensure last pulse is output.
        input_rising   = input_rising[:-1]
        input_falling  = input_falling[:-1]
    return input_rising, input_falling, output_rising, output_falling

# A function I'll use later to extract FPGA resource usage stats from Yosys log output.
def print_stats(yosys_log):
    stat_start_line = yosys_log.grep(r'^2\.27\. ')
    stat_end_line = yosys_log.grep(r'^2\.28\. ')
    start_index = yosys_log.index(stat_start_line[0])
    end_index = yosys_log.index(stat_end_line[0])
    print('\n'.join(yosys_log[start_index+2:end_index-1]))


from pygmyhdl import *


def ram(clk_i, en_i, wr_i, addr_i, data_i, data_o):
    '''
    Inputs:
      clk_i:  Data is read/written on the rising edge of this clock input.
      en_i:   When high, the RAM is enabled for read/write operations.
      wr_i:   When high, data is written to the RAM; when low, data is read from the RAM.
      addr_i: Address bus for selecting which RAM location is being read/written.
      data_i: Data bus for writing data into the RAM.
    Outputs:
      data_o: Data bus for reading data from the RAM.
    '''
    
    # Create an array of words to act as RAM locations for storing data.
    # The number of bits in each word is set by the width of the data input bus.
    # The number of words is determined by the width of the address bus so,
    # for example, a 4-bit address would create 2**4 = 16 RAM locations.
    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    
    # Perform read/write operations on the rising edge of the clock.
    @seq_logic(clk_i.posedge)
    def logic():
        if en_i:
            # The read/write operations only get executed if the enable input is high.
            if wr_i:
                # If the write-control is high, write the value on the input data bus
                # into the array of words at the given address value.
                mem[addr_i.val].next = data_i
            else:
                # If the write-control is low, read data from the word at the
                # given address value and send it to the output data bus.
                data_o.next = mem[addr_i.val]


initialize()  # Yeah, yeah, get things ready for simulation...

# Create wires and buses to connect to the RAM.
clk = Wire(name='clk')
en = Wire(name='en')
wr = Wire(name='wr')
addr = Bus(8, name='addr')
data_i = Bus(8, name='data_i')
data_o = Bus(8, name='data_o')

# Instantiate the RAM.
ram(clk_i=clk, en_i=en, wr_i=wr, addr_i=addr, data_i=data_i, data_o=data_o)

def ram_test_bench():
    '''RAM test bench: write 10 values to RAM, then read them back.'''
    
    en.next = 1  # Enable the RAM.
    
    # Write data to the first 10 locations in the RAM.
    wr.next = 1  # Enable writes to RAM.
    for i in range(10):
        addr.next = i            # Select RAM location to be written.
        data_i.next = 3 * i + 1  # Generate a value to write to the location.
        
        # Pulse the clock to write the data to RAM.
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

    # Read data from the 10 locations that were written.
    wr.next = 0  # Disable writes to RAM == enable reads from RAM.
    for i in range(10):
        addr.next = i   # Select the RAM location to be read.
        
        # Pulse the clock to read the data from RAM.
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

# Simulate the RAM using the test bench.
simulate(ram_test_bench())

# Look at the RAM inputs and outputs as the simulation was executed.
show_text_table('en clk wr addr data_i data_o')


toVerilog(ram, clk_i=Wire(), en_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))



log = !yosys -p "synth_ice40" ram.v
print_stats(log)                     # Just print the FPGA resource usage stats from the log output.


def ram(clk_i,wr_i, addr_i, data_i, data_o):
    '''
    Inputs:
      clk_i:  Data is read/written on the rising edge of this clock input.
      wr_i:   When high, data is written to the RAM; when low, data is read from the RAM.
      addr_i: Address bus for selecting which RAM location is being read/written.
      data_i: Data bus for writing data into the RAM.
    Outputs:
      data_o: Data bus for reading data from the RAM.
    '''
    
    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[addr_i.val].next = data_i
        else:
            data_o.next = mem[addr_i.val]
                
toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))

log = !yosys -p "synth_ice40" ram.v
print_stats(log)



def simpler_ram(clk_i,wr_i, addr_i, data_i, data_o):
    '''
    Inputs:
      clk_i:  Data is read/written on the rising edge of this clock input.
      wr_i:   When high, data is written to the RAM; when low, data is read from the RAM.
      addr_i: Address bus for selecting which RAM location is being read/written.
      data_i: Data bus for writing data into the RAM.
    Outputs:
      data_o: Data bus for reading data from the RAM.
    '''
    
    mem = [Bus(len(data_i)) for _ in range(2**len(addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[addr_i.val].next = data_i
        data_o.next = mem[addr_i.val]  # RAM address is always read out!
                
toVerilog(simpler_ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(8), data_i=Bus(8), data_o=Bus(8))

log = !yosys -p "synth_ice40" simpler_ram.v
print_stats(log)



def dualport_ram(clk_i, wr_i, wr_addr_i, rd_addr_i, data_i, data_o):
    '''
    Inputs:
      clk_i:     Data is read/written on the rising edge of this clock input.
      wr_i:      When high, data is written to the RAM; when low, data is read from the RAM.
      wr_addr_i: Address bus for selecting which RAM location is being written.
      rd_addr_i: Address bus for selecting which RAM location is being read.
      data_i:    Data bus for writing data into the RAM.
    Outputs:
      data_o:    Data bus for reading data from the RAM.
    '''
    
    mem = [Bus(len(data_i)) for _ in range(2**len(wr_addr_i))]
    
    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[wr_addr_i.val].next = data_i
        data_o.next = mem[rd_addr_i.val]  # Read from a different location than write.



initialize()

# Create wires and buses to connect to the dual-port RAM.
clk = Wire(name='clk')
wr = Wire(name='wr')
wr_addr = Bus(8, name='wr_addr')  # Address bus for writes.
rd_addr = Bus(8, name='rd_addr')  # Second address bus for reads.
data_i = Bus(8, name='data_i')
data_o = Bus(8, name='data_o')

# Instantiate the RAM.
dualport_ram(clk_i=clk, wr_i=wr, wr_addr_i=wr_addr, rd_addr_i=rd_addr, data_i=data_i, data_o=data_o)

def ram_test_bench():
    for i in range(10):  # Perform 10 RAM writes and reads.
        
        # Write data to address i.
        wr_addr.next = i
        data_i.next = 3 * i + 1
        wr.next = 1
        
        # Read data from address i-3. After three clocks, the data that entered
        # on the data_i bus will start to appear on the data_o bus.
        rd_addr.next = i - 3
        
        # Pulse the clock to trigger the write and read operations.
        clk.next = 0
        yield delay(1)
        clk.next = 1
        yield delay(1)

# Simulate the RAM using the test bench.
simulate(ram_test_bench())

# Look at the RAM inputs and outputs as the simulation was executed.
show_text_table('clk wr wr_addr data_i rd_addr data_o')


toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(9), data_i=Bus(10), data_o=Bus(10))
log = !yosys -p "synth_ice40" ram.v
print_stats(log)


toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(7), data_i=Bus(24), data_o=Bus(24))
log = !yosys -p "synth_ice40" ram.v
print_stats(log)


toVerilog(ram, clk_i=Wire(), wr_i=Wire(), addr_i=Bus(9), data_i=Bus(24), data_o=Bus(24))
log = !yosys -p "synth_ice40" ram.v
print_stats(log)


def gen_reset(clk_i, reset_o):
    '''
    Generate a reset pulse to initialize everything.
    Inputs:
        clk_i:   Input clock.
    Outputs:
        reset_o: Active-high reset pulse.
    '''
    cntr = Bus(1)  # Reset counter.
    
    @seq_logic(clk_i.posedge)
    def logic():
        if cntr < 1:
            # Generate a reset while the counter is less than some threshold
            # and increment the counter.
            cntr.next = cntr.next + 1
            reset_o.next = 1
        else:
            # Release the reset once the counter passes the threshold and
            # stop incrementing the counter.
            reset_o.next = 0


def sample_en(clk_i, do_sample_o, frq_in=12e6, frq_sample=100):
    '''
    Send out a pulse every so often to trigger a sampling operation.
    Inputs:
        clk_i:      Input clock.
        frq_in:     Frequency of the input clock (defaults to 12 MHz).
        frq_sample: Frequency of the sample clock (defaults to 100 Hz).
    Outputs:
        do_sample_o: Sends out a single-cycle pulse every 1/frq_sample seconds.
    '''
    # Compute the width of the counter and when it should roll-over based
    # on the master clock frequency and the desired sampling frequency.
    from math import ceil, log2
    rollover = int(ceil(frq_in / frq_sample)) - 1
    cntr = Bus(int(ceil(log2(frq_in/frq_sample))))
    
    # Sequential logic for generating the sampling pulse.
    @seq_logic(clk_i.posedge)
    def counter():
        cntr.next = cntr + 1         # Increment the counter.
        do_sample_o.next = 0         # Clear the sampling pulse output except...
        if cntr == rollover:
            do_sample_o.next = 1     # ...when the counter rolls over.
            cntr.next = 0 


def record_play(clk_i, button_a, button_b, leds_o):
    '''
    Sample value on button B input, store in RAM, and playback by turning LEDs on/off.
    Inputs:
        clk_i:    Clock input.
        button_a: Button A input. High when pressed. Controls record/play operation.
        button_b: Button B input. High when pressed. Used to input samples for controlling LEDs.
    Outputs:
        leds_o:   LED outputs.
    '''
    
    # Instantiate the reset generator.
    reset = Wire()
    gen_reset(clk_i, reset)
    
    # Instantiate the sampling pulse generator.
    do_sample = Wire()
    sample_en(clk_i, do_sample)
    
    # Instantiate a RAM for holding the samples.
    wr = Wire()
    addr = Bus(11)
    end_addr = Bus(len(addr)) # Holds the last address of the recorded samples.
    data_i = Bus(1)
    data_o = Bus(1)
    ram(clk_i, wr, addr, data_i, data_o)
    
    # States of the record/playback controller.
    state = Bus(3)         # Holds the current state of the controller.
    INIT = 0               # Initialize. The reset pulse sends us here.
    WAITING_TO_RECORD = 1  # Getting read to record samples.
    RECORDING = 2          # Actually storing samples in RAM.
    WAITING_TO_PLAY = 3    # Getting ready to play back samples.
    PLAYING = 4            # Actually playing back samples.

    # Sequential logic for the record/playback controller.
    @seq_logic(clk_i.posedge)
    def fsm():
        
        wr.next = 0        # Keep the RAM write-control off by default.
        
        if reset:  # Initialize the controller using the pulse from the reset generator.
            state.next = INIT  # Go to the INIT state after the reset is released.
            
        elif do_sample:  # Process a sample whenever the sampling pulse arrives.
        
            if state == INIT:  # Initialize the controller.
                leds_o.next = 0b10101  # Light LEDs to indicate the INIT state.
                if button_a == 1:
                    # Get ready to start recording when button A is pressed.
                    state.next = WAITING_TO_RECORD  # Go to record setup state.
                    
            elif state == WAITING_TO_RECORD:  # Setup for recording.
                leds_o.next = 0b11010  # Light LEDs to indicate this state.
                if button_a == 0:
                    # Start recording once button A is released.
                    addr.next = 0           # Start recording from beginning of RAM.
                    data_i.next = button_b  # Record the state of button B.
                    wr.next = 1             # Write button B state to RAM.
                    state.next = RECORDING  # Go to recording state.
                    
            elif state == RECORDING:  # Record samples of button B to RAM.
                addr.next = addr + 1    # Next location for storing sample.
                data_i.next = button_b  # Sample state of button B.
                wr.next = 1             # Write button B state to RAM.
                # For feedback to the user, display the state of button B on the LEDs.
                leds_o.next = concat(1,button_b, button_b, button_b, button_b)
                if button_a == 1:
                    # If button A pressed, then get ready to play back the stored samples.
                    end_addr.next = addr+1  # Store the last sample address.
                    state.next = WAITING_TO_PLAY  # Go to playback setup state.
                    
            elif state == WAITING_TO_PLAY:  # Setup for playback.
                leds_o.next = 0b10000  # Light LEDs to indicate this state.
                if button_a == 0:
                    # Start playback once button A is released.
                    addr.next = 0         # Start playback from beginning of RAM.
                    state.next = PLAYING  # Go to playback state.
                    
            elif state == PLAYING:  # Show recorded state of button B on the LEDs.
                leds_o.next = concat(1,data_o[0],data_o[0],data_o[0],data_o[0])
                addr.next = addr + 1  # Advance to the next sample.
                if addr == end_addr:
                    # Loop back to the start of RAM if this is the last sample.
                    addr.next = 0
                if button_a == 1:
                    # Record a new sample if button A is pressed.
                    state.next = WAITING_TO_RECORD



toVerilog(record_play, clk_i=Wire(), button_a=Wire(), button_b=Wire(), leds_o=Bus(5))

with open('record_play.pcf', 'w') as pcf:
    pcf.write(
'''
set_io clk_i 21
set_io leds_o[0] 99
set_io leds_o[1] 98
set_io leds_o[2] 97
set_io leds_o[3] 96
set_io leds_o[4] 95
set_io button_a 118
set_io button_b 114
'''
    )


!yosys -q -p "synth_ice40 -blif record_play.blif" record_play.v
!arachne-pnr -q -d 1k -p record_play.pcf record_play.blif -o record_play.asc
!icepack record_play.asc record_play.bin
!iceprog record_play.bin

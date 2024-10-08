import Component
import Buffer_cell
from Network import Network
from Hardware import Hardware
from Config import Config
import math

class Buffer(Component.Component):
    def __init__(self, component_name, model_key):
        """
        Initialize the Buffer with its name and model configuration.
        
        Parameters:
        component_name (str): The name of the Buffer component.
        model_key (str): The model key to look up in the configuration.
        """
        super().__init__(component_name, model_key)
        self._buffer_cell = Buffer_cell.BufferCell("BufferCell", "buffer_model")  # One buffer cell
        
        if Network.type == "CNN":
            self._weight_precision = Hardware.weight_precision
            self.bus_size = int(Config.config[component_name]["bus_size"])
            self._kernel_size = Network.kernel_size
            self.memory_bit_size = self._weight_precision * self._kernel_size * Hardware.parallelism_level
            self.memory_size = self.convert_size(self.memory_bit_size)
            self.read_power_per_weight = self._buffer_cell.read_power * self._weight_precision
            self.write_power_per_weight = self._buffer_cell.write_power * self._weight_precision
            self.read_delay_per_weight = self._buffer_cell.read_delay  
            self.write_delay_per_weight = self._buffer_cell.write_delay 
            self.number_of_weight_read_per_clock = self.bus_size / self._weight_precision

            self.read_per_kernel = self.read_power()
            self.write_per_kernel = self.write_power()
            self.shift_power_per_kernel = self.shift_power()

            self.total_write_power = self.write_power_per_weight * Network.total_weights
            self.total_read_power = Network.output_feature_map_height * self.read_power_per_weight * Network.kernel_size * math.ceil(Network.output_feature_map_width / Network.kernel_width)

            self.total_write_clock = Network.total_weights / self.number_of_weight_read_per_clock
            self.total_read_clock = Network.output_feature_map_height * math.ceil(Network.output_feature_map_width / Network.kernel_width)
            self.total_write_delay = self.total_write_clock * self.write_delay_per_weight 
            self.total_read_delay = (self.total_read_clock * self.read_delay_per_weight)/Hardware.parallelism_level
            self.delay_per_kernel = self._buffer_cell.read_delay 
            self.total_delay = self.delay + self._buffer_cell.total_delay       
            self.total_power = self.power + (self._buffer_cell.total_power * self.memory_bit_size)  # Static power of memory 
            self.total_area = self.area + (self.memory_bit_size * self._buffer_cell.total_area)
        else:
            self.read_power_per_weight = 0
            self.write_power_per_weight = 0
            self.read_delay_per_weight = 0
            self.write_delay_per_weight = 0
            
            self.total_write_power = 0
            self.total_read_power = 0

            self.total_write_delay = 0
            self.total_read_delay = 0
            self.total_delay = 0
            self.total_power = 0
            self.total_area = 0

    def read_power(self):
        """
        Calculate the read power for the kernel.
        
        Returns:
        float: The read power for the kernel.
        """
        return self._kernel_size * self.read_power_per_weight
    
    def write_power(self):
        """
        Calculate the write power for the kernel.
        
        Returns:
        float: The write power for the kernel.
        """
        return self._kernel_size * self.write_power_per_weight
    
    def shift_power(self):
        """
        Calculate the shift power for the kernel.
        
        Returns:
        float: The shift power for the kernel.
        """
        return self.read_power()  # + self.write_power()

    def convert_size(self, size_in_bits):
        """
        Convert a size from bits to more readable units (KB, MB, GB, etc.)
        
        Parameters:
        size_in_bits (int): Size in bits
        
        Returns:
        str: A string representing the size in a more readable format
        """
        # Define the conversion constants
        B = 8
        KB = 1024 * B  # 1 Kilobyte = 1024 * 8 bits
        MB = KB * 1024  # 1 Megabyte = 1024 Kilobytes
        GB = MB * 1024  # 1 Gigabyte = 1024 Megabytes
        TB = GB * 1024  # 1 Terabyte = 1024 Gigabytes

        # Convert the size to a more readable format
        if size_in_bits >= TB:
            return f"{size_in_bits / TB:.2f} TB"
        elif size_in_bits >= GB:
            return f"{size_in_bits / GB:.2f} GB"
        elif size_in_bits >= MB:
            return f"{size_in_bits / MB:.2f} MB"
        elif size_in_bits >= KB:
            return f"{size_in_bits / KB:.2f} KB"
        elif size_in_bits >= B:
            return f"{size_in_bits / B:.2f} Bytes"
        else:
            return f"{size_in_bits} bits"

    def print_detail(self, tab=""):
        """
        Print the details of the Buffer component.
        
        Parameters:
        tab (str): The tab character(s) to prepend to each line. Default is an empty string.
        
        Returns:
        str: A string representation of the component details.
        """
        result = super().print_detail(tab)
        tab += '\t'
        result += self._buffer_cell.print_detail(tab)
        return result

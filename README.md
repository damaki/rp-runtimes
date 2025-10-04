# RP2040 Runtimes

This repository generates Ada/SPARK runtimes for the Raspberry Pi RP2040.

The following runtime profiles are supported:
* light-tasking
* embedded

The runtime supports multitasking across both of the Cortex-M0+ cores on the
RP2040. By default, tasks run on the first core. Tasks can be pinned to the
second core using the `CPU` aspect in the task declaration.
For example, to declare a task that runs on the second core:

```ada
task My_Task with CPU => 2;
```

Interrupt handlers can also be assigned execute on a specific core on a
per-interrupt basis.
Each interrupt in package `Ada.Interrupts.Names` has two variants: the
ones ending in `_CPU_1` are executed on the first core, and the ones ending
in `_CPU_2` are executed on the second core.
For example, to handle the `PIO0_IRQ_0` interrupt on the second core:

```ada
protected My_PO with Interrupt_Priority => System.Interrupt_Priority'Last is

   --  Declare public protected subprograms here

private

   procedure PIO0_Interrupt_Handler with
     Attach_Handler => Ada.Interrupts.Names.PIO0_IRQ_0_Interrupt_CPU_2;

end My_PO;
```

>[!TIP]
>If you don't want the runtime to use the second core, then you can configure
>the runtime to only use the first core by setting the `Max_CPUs` crate
>configuration variable to `1`. See section "General Configuration" below.

## Usage

Using the `light_tasking_rp2040` runtime as an example, first edit your
`alire.toml` file and add the following elements:
 - Add `light_tasking_rp2040` in the dependency list:
   ```toml
   [[depends-on]]
   light_tasking_rp2040 = "*"
   ```

Then edit your project file to add the following elements:
 - "with" the run-time project file:
   ```ada
   with "runtime_build.gpr";
   ```
 - specify the `Target` and `Runtime` attributes:
   ```ada
   for Target use Runtime_Build'Target;
   for Runtime ("Ada") use Runtime_Build'Runtime ("Ada");
   ```
 - specify the `Linker` switches:
   ```ada
   package Linker is
     for Switches ("Ada") use Runtime_Build.Linker_Switches;
   end Linker;
   ```

>[!TIP]
> It is also recommended to add `--gc-sections` to your linker switches to
> remove any unused code and data.
> ```ada
>    package Linker is
>      for Switches ("Ada") use Runtime_Build.Linker_Switches & ("-Wl,--gc-sections");
>    end Linker;
> ```

## Resources Used

The light-tasking and embedded runtime profiles use one of the ALARM interrupts
(configurable)
to implement Ada semantics for time, i.e., delay statements and the package
Ada.Real_Time. The timer interrupt runs at the highest priority.

The runtime can be configured to use one or both of the RP2040's CPU cores
(see "Runtime Configuration" below).
When the runtime is configured for both cores then the runtime takes care
of starting the second core and scheduling tasks on it. When the runtime is
configured for a single core, then it completely ignores the second core.

## Runtime Configuration

The runtime can be configured by setting various crate configuration variables
in your `alire.toml`. The available configuration options are described in the
following subsections

### General Configuration

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>Time_Base</tt></td>
    <td>
      <tt>"ALARM0"</tt><br/>
      <tt>"ALARM1"</tt><br/>
      <tt>"ALARM2"</tt><br/>
      <tt>"ALARM3"</tt><br/>
    </td>
    <td><tt>"ALARM3"</tt></td>
    <td>
      Selects which ALARM interrupt the runtime uses to implement the semantics
      of <tt>Ada.Real_Time</tt>. The specified ALARM interrupt will be reserved
      by the runtime and will not be available for use by the user program.
    </td>
  </tr>
  <tr>
    <td><tt>Max_CPUs</tt></td>
    <td>
      <tt>1</tt>, <tt>2</tt>
    </td>
    <td><tt>2</tt></td>
    <td>
      Selects how many of the RP2040 cores are used by the runtime.
      By default, the runtime uses both cores and tasks can be assigned to either
      core using the <tt>CPU</tt> pragma or aspect on the task declaration. For example:
      <tt>task My_Task with CPU => 2;</tt> runs <tt>My_Task</tt> on the second core.<br/>
      When this is set to 1, the runtime will ignore the second CPU and will
      schedule all tasks and interrupts on the first core.
    </td>
  </tr>
</table>

For example, to configure the light-tasking-rp2040 runtime to only use the
first core, add this to your `alire.toml`:
your `alire.toml`:
```toml
[configuration.values]
light_tasking_rp2040.Max_CPUs = 1
```

### Clock Configuration

The following variables can be set to change the `pll_sys` clock configuration.
By default, a 125 MHz clock is generated, assuming a 12 MHz XOSC.

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>PLL_Sys_Reference_Div</tt></td>
    <td><tt>1 .. 63</tt></td>
    <td><tt>1</tt></td>
    <td>
      Sets the REFDIV for <tt>pll_sys</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_Sys_VCO_Multiple</tt></td>
    <td><tt>16 .. 320</tt></td>
    <td><tt>125</tt></td>
    <td>
      Sets the VCO multiplier for <tt>pll_sys</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_Sys_Post_Div_1</tt></td>
    <td><tt>1 .. 7</tt></td>
    <td><tt>6</tt></td>
    <td>
      Sets POSTDIV1 for <tt>pll_sys</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_Sys_Post_Div_2</tt></td>
    <td><tt>1 .. 7</tt></td>
    <td><tt>2</tt></td>
    <td>
      Sets POSTDIV2 for <tt>pll_sys</tt>
    </td>
  </tr>
</table>

The following variables can be set to change the `pll_usn` clock configuration.
By default, a 48 MHz USB clock is generated assuming a 12 MHz XOSC.

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>PLL_USB_Reference_Div</tt></td>
    <td><tt>1 .. 63</tt></td>
    <td><tt>1</tt></td>
    <td>
      Sets the REFDIV for <tt>pll_usb</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_USB_VCO_Multiple</tt></td>
    <td><tt>16 .. 320</tt></td>
    <td><tt>40</tt></td>
    <td>
      Sets the VCO multiplier for <tt>pll_usb</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_USB_Post_Div_1</tt></td>
    <td><tt>1 .. 7</tt></td>
    <td><tt>5</tt></td>
    <td>
      Sets POSTDIV1 for <tt>pll_usb</tt>
    </td>
  </tr>
  <tr>
    <td><tt>PLL_USB_Post_Div_2</tt></td>
    <td><tt>1 .. 7</tt></td>
    <td><tt>2</tt></td>
    <td>
      Sets POSTDIV2 for <tt>pll_usb</tt>
    </td>
  </tr>
</table>

For example, to configure a 133 MHz clock add the following to your `alire.toml`:
```toml
[configuration.values]
light_tasking_rp2040.PLL_Sys_Reference_Div = 1
light_tasking_rp2040.PLL_Sys_VCO_Multiple = 133
light_tasking_rp2040.PLL_Sys_Post_Div_1 = 6
light_tasking_rp2040.PLL_Sys_Post_Div_2 = 2
```

### Board Configuration

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>Board</tt></td>
    <td>
      <tt>"generic_board"</tt></br>
      <tt>"rpi_pico"</tt></br>
      <tt>"adafruit_feather_rp2040"</tt></br>
      <tt>"adafruit_itsybitsy_rp2040"</tt></br>
      <tt>"adafruit_macropad_rp2040"</tt></br>
      <tt>"adafruit_qt2040_trinkey"</tt></br>
      <tt>"adafruit_qtpy_rp2040"</tt></br>
      <tt>"arduino_nano_rp2040_connect"</tt></br>
      <tt>"pimoroni_interstate75"</tt></br>
      <tt>"pimoroni_keybow2040"</tt></br>
      <tt>"pimoroni_pga2040"</tt></br>
      <tt>"pimoroni_picolipo_4m"</tt></br>
      <tt>"pimoroni_picolipo_16m"</tt></br>
      <tt>"pimoroni_picosystem"</tt></br>
      <tt>"pimoroni_plasma2040"</tt></br>
      <tt>"pimoroni_tiny2040"</tt></br>
      <tt>"sparkfun_micromod"</tt></br>
      <tt>"sparkfun_promicro"</tt></br>
      <tt>"sparkfun_thingplus"</tt></br>
    </td>
    <td><tt>"rpi_pico"</tt></td>
    <td>
      Configures the runtime for a specific board. This is used to select the
      appropriate second-stage bootloader and linker script based on the
      flash chip mounted on the board.<br/>
      When <tt>"generic_board"</tt> is selected, the board parameters must be
      set manually (see below).
    </td>
  </tr>
</table>

When `"generic_board"` is selected as the board, then the following configuration
variables can be set to specify the board parameters.
These variables are ignored for non-generic boards.

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>XOSC_Frequency</tt></td>
    <td>
      Any non-negative value
    </td>
    <td><tt>12000000</tt></td>
    <td>
      Specifies the frequency of the on-board XOSC in Hertz. Set to 0 if the
      board does not have an XOSC.
    </td>
  </tr>
  <tr>
    <td><tt>XOSC_Startup_Delay_Mult</tt></td>
    <td>
      <tt>1 .. 16383</tt>
    </td>
    <td><tt>64</tt></td>
    <td>
      Sets the startup delay for the XOSC in milliseconds.
    </td>
  </tr>
  <tr>
    <td><tt>Flash_Chip</tt></td>
    <td>
      <tt>"generic_qspi_128"</tt><br/>
      <tt>"at25sf128a"</tt><br/>
      <tt>"gd25q64c"</tt><br/>
      <tt>"w25q16jv"</tt><br/>
      <tt>"w25q32jv"</tt><br/>
      <tt>"w25q64jv"</tt><br/>
      <tt>"w25q128jv"</tt><br/>
    </td>
    <td><tt>"generic_qspi_128"</tt></td>
    <td>
      Sets the flash chip that is fitted on the board. This is used to select
      the appropriate second-stage bootloader and set the flash memory size in
      the linker script.
    </td>
  </tr>
</table>

### Interrupt Stack Configuration

The following variables configure the interrupt stacks:

<table>
  <thead>
    <th>Variable</th>
    <th>Values</th>
    <th>Default</th>
    <th>Description</th>
  </thead>
  <tr>
    <td><tt>Interrupt_Stack_Size</tt></td>
    <td>
      Any positive integer
    </td>
    <td><tt>1024</tt></td>
    <td>
      Sets the size of the primary stack used for interrupt handlers in bytes.
    </td>
  </tr>
  <tr>
    <td><tt>Interrupt_Secondary_Stack_Size</tt></td>
    <td>
      Any positive integer
    </td>
    <td><tt>128</tt></td>
    <td>
      Sets the size of the secondary stack used for interrupt handlers in bytes.
    </td>
  </tr>
</table>

>[!NOTE]
> The primary and secondary stack sizes for tasks can be set via the
> `Storage_Size` and `Secondary_Stack_Size` pragmas/aspects respectively on the
> task declaration.
>
>

### GPR Scenario Variables

The runtime project files expose `*_BUILD` and and `*_LIBRARY_TYPE` GPR
scenario variables to configure the build mode (e.g. debug/production) and
library type. These variables are prefixed with the name of the runtime in
upper case. For example, for the light-tasking-rp2040 runtime the variables
are `LIGHT_TASKING_RP2040_BUILD` and `LIGHT_TASKING_RP2040_LIBRARY_TYPE`
respectively.

The `*_BUILD` variable can be set to the following values:
* `Production` (default) builds the runtime with optimization enabled and with
  all run-time checks suppressed.
* `Debug` disables optimization and adds debug symbols.
* `Assert` enables assertions.
* `Gnatcov` disables optimization and enables flags to help coverage.

The `*_LIBRARY_TYPE` variable can be set to either `static` (default) or
`dynamic`, though only `static` libraries are supported on this target.

You can usually leave these set to their defaults, but if you want to set them
explicitly then you can set them either by passing them on the command line
when building your project with Alire:
```sh
alr build -- -XLIGHT_TASKING_RP2040_BUILD=Debug
```

or by setting them in your project's `alire.toml`:
```toml
[gpr-set-externals]
LIGHT_TASKING_RP2040_BUILD = "Debug"
```
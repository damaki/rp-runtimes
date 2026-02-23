# RP2040 and RP2350 Runtimes

This repository contains the sources to generate Ada/SPARK runtimes for the GNAT
compiler, targeting the Raspberry Pi RP2040 and RP2350 microcontrollers.

The following runtime profiles are supported
(see the [GNAT User's Guide Supplement for Cross Platforms](https://docs.adacore.com/live/wave/gnat_ugx/html/gnat_ugx/gnat_ugx/gnat_runtimes.html)
for more details):
* light
* light-tasking
* embedded

The complete list of available runtimes are:
* `light_rp2040`
* `light_rp2350`
* `light_tasking_rp2040`
* `light_tasking_rp2350`
* `embedded_rp2040`
* `embedded_rp2350`

These runtimes are configurable via Alire crate configuration variables.
See [README-RP2040.md](README-RP2040.md) and [README-RP2350.md](README-RP2350.md)
for details on the runtimes.

## Usage

The pre-generated runtimes are distributed as crates in the Alire community
index. This section describes how to set up your project to use one of those
crates.

Using the `light_tasking_rp2040` runtime as an example, first edit your
`alire.toml` file and add the following elements:
 - Add `light_tasking_rp2040` in the dependency list:
   ```toml
   [[depends-on]]
   light_tasking_rp2040 = "*"
   ```

Then edit your project file to add the following elements:
 - "with" the run-time project files:
   ```ada
   with "runtime_build.gpr";
   with "ravenscar_build.gpr";
   ```
 - specify the `Target` and `Runtime` attributes:
   ```ada
   for Target use Runtime_Build'Target;
   for Runtime ("Ada") use Runtime_Build'Runtime ("Ada");
   ```
 - specify the `Linker` switches:
   ```ada
   package Linker is
     for Switches ("Ada") use Runtime_Build.Linker_Switches & ("-Wl,--gc-sections");
   end Linker;
   ```

>[!TIP]
> The `--gc-sections` linker switch is recommended (but not mandatory) to
> remove any unused code and data sections from the executable and therefore
> reduce memory usage.

## Multitasking

The _light-tasking_ and _embedded_ runtime profiles support multitasking across
both cores on the RP2040/RP2350 using the Ada language's task and protected
object mechanisms. By default, tasks run on the first core. Tasks can be pinned
to the second core using the `CPU` aspect or pragma in the task declaration.
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
>configuration variable to `1`. See [README-RP2040.md](README-RP2040.md) and
>[README-RP2350.md](README-RP2350.md). The _light_ runtime profile always uses
>1 core.
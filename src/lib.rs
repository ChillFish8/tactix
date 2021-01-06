#[macro_use]
extern crate lazy_static;

mod actor;
mod runtime;
mod handle;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use mimalloc::MiMalloc;
use std::thread;

#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;

#[pyclass]
pub struct TactixRuntime {
    handle: thread::JoinHandle<()>,
}

#[pymethods]
impl TactixRuntime {
    #[new]
    fn new() -> Self {
        let handle = runtime::start_background();
        Self { handle }
    }

    fn wait(&self) {
        let _ = self.handle.join();
    }

    fn shutdown(&self) {
        runtime::RUNTIME.shutdown_background();
    }
}


///
/// Wraps all our existing pyobjects together in the module
///
#[pymodule]
fn tactix(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<TactixRuntime>()?;
    m.add_class::<actor::TactixActor>()?;
    Ok(())
}
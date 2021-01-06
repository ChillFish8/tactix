#[macro_use]
extern crate lazy_static;

mod actor;
mod runtime;
mod handle;

use pyo3::prelude::*;

use mimalloc::MiMalloc;
use tokio::sync::mpsc::UnboundedSender;

use std::sync::mpsc;


#[global_allocator]
static GLOBAL: MiMalloc = MiMalloc;


#[pyclass]
struct TactixRuntime {
    stop: UnboundedSender<()>,
    wait: mpsc::Receiver<()>,
}

#[pymethods]
impl TactixRuntime {
    #[new]
    fn new() -> Self {
        let (stop, wait) = runtime::start_background();
        Self { stop, wait }
    }

    fn wait(&mut self) {
        if let Err(e) = self.wait.recv() {
            eprintln!("{:?}", e)
        }
    }

    fn shutdown(&self) {
        let _ = self.stop.send(());
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
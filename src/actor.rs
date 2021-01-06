use pyo3::prelude::*;

use tokio::sync::mpsc::unbounded_channel;
use tokio::task::JoinHandle;

use crate::runtime;
use crate::handle::{Sender, Handler};


#[pyclass]
pub struct TactixActor {
    tx: Sender,  // event, message, delay
    handle: JoinHandle<()>
}

#[pymethods]
impl TactixActor {
    #[new]
    fn new(on_message: PyObject) -> Self {
        let (tx, rx) = unbounded_channel();

        let handle = Handler::watch(rx, on_message);

        Self { tx, handle }
    }

    fn send(&self, event: PyObject, message: PyObject) {
        Handler::send(&self.tx, (event, message));
    }

    fn send_later(&self, event: PyObject, message: PyObject, delay: f64) {
        runtime::spawn(Handler::send_later(
            self.tx.clone(),
            (event, message),
            delay
        ));
    }

    fn shutdown(&self) {
        self.handle.abort();
    }
}








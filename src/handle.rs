use pyo3::{PyObject, Python};

use tokio::sync::mpsc::{UnboundedSender, UnboundedReceiver};
use tokio::time;

use std::time::Duration;
use std::sync::Arc;

use crate::runtime;

pub type Payload = (PyObject, PyObject);
pub type Sender = UnboundedSender<Payload>;
pub type Receiver = UnboundedReceiver<Payload>;


pub struct Handler;
impl Handler {
    pub async fn send_later(sender: Sender, payload: Payload, delay: f64) {
        time::sleep(Duration::from_secs_f64(delay)).await;
        send(&sender, payload);
    }

    pub fn send(tx: &Sender, payload: Payload) {
        if let Err(_) = tx.send(payload) {
            eprintln!("Actor disconnected while pending!");
        };
    }
}

impl Handler {
    pub async fn watch(mut rx: Receiver, cb: PyObject) {
        let cb = Arc::new(cb);
        while Some(msg) = rx.recv().await {
            runtime::spawn(Self::invoke_cb(
                cb.clone(),
                msg,
            ))
        }
    }

    async fn invoke_cb(cb: Arc<PyObject>, payload: Payload) {
        Python::with_gil(|py| {
            let _ = cb.call1(py, payload);
        });
    }
}


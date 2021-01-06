use pyo3::{PyObject, Python};

use tokio::sync::mpsc::{UnboundedSender, UnboundedReceiver};
use tokio::time;
use tokio::task::JoinHandle;

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
        Self::send(&sender, payload);
    }

    pub fn send(tx: &Sender, payload: Payload) {
        if let Err(_) = tx.send(payload) {
            eprintln!("Actor disconnected while pending!");
        };
    }
}

impl Handler {
    pub fn watch(rx: Receiver, cb: PyObject) -> JoinHandle<()> {
        runtime::spawn(Self::_watch(rx, cb))
    }

    async fn _watch(mut rx: Receiver, cb: PyObject) {
        let cb = Arc::new(cb);
        while let Some(msg) = rx.recv().await {
            let _ = runtime::spawn(Self::invoke_cb(
                cb.clone(),
                msg,
            ));
        }
    }

    async fn invoke_cb(cb: Arc<PyObject>, payload: Payload) {
        Python::with_gil(|py| {
            if let Err(e) = cb.call1(py, payload) {
                println!("{:?}", e);
            }
        });
        println!("no-deadlocked")
    }
}


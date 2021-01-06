use tokio::runtime::{Builder, Runtime};
use futures::Future;

use tokio::task::JoinHandle;
use tokio::sync::mpsc::{unbounded_channel, UnboundedSender};

use std::thread;
use std::sync::mpsc::{sync_channel, Receiver};


lazy_static! {
    pub static ref RUNTIME: Runtime = {
        Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed runtime sanity check.")
    };
}

pub fn spawn<F>(future: F) -> JoinHandle<F::Output>
    where F: Future + Send + 'static,
          F::Output: Send + 'static,
{
    RUNTIME.spawn(future)
}


pub fn start_background() -> (UnboundedSender<()>, Receiver<()>) {
    let (set, mut waiter) = unbounded_channel::<()>();
    let (tx, rx) = sync_channel::<()>(0);
    let _ = thread::spawn(move || {
        RUNTIME.block_on(waiter.recv());
        let _ = tx.send(());
    });

    (set, rx)
}


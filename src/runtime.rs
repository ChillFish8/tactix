use tokio::runtime::{Builder, Runtime};
use futures::Future;
use tokio::task::JoinHandle;
use std::thread;


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

pub fn start_background() -> thread::JoinHandle<()> {
    thread::spawn(move || {
        let fut = futures::future::pending::<()>();
        RUNTIME.block_on(fut);
    })
}


use pyo3::prelude::*;

trait Actor {
    type Response = PyResult<()>;

    fn send(&self, event: PyObject, message: PyObject) -> Self::Response;

    fn shutdown(&self);
}
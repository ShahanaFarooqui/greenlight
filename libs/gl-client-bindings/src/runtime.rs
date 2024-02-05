use tokio::runtime::{Builder, Runtime};
use std::future::Future;
use once_cell::sync::OnceCell;

static TOKIO_RUNTIME: OnceCell<Runtime> = OnceCell::new();

pub(crate) fn get_runtime<'a>() -> &'a Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        let mut builder = Builder::new_multi_thread();
        builder.enable_all();
        builder.build().expect("Unable to build Tokio runtime")
    })
}

pub(crate) fn exec<F, T>(f: F) -> T
where
    F: Future<Output = T> + Sized + Send,
    T: Send,
{
    get_runtime().block_on(f)
}

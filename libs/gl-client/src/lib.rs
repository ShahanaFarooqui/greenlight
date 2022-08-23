//! Greenlight client library to schedule nodes, interact with them
//! and sign off on signature requests.
//!

extern crate anyhow;

#[macro_use]
extern crate log;

/// Interact with a node running on greenlight.
///
/// The node must be scheduled using [`crate::scheduler::Scheduler`]:
///
///
pub mod node;

/// Generated protobuf messages and client stubs.
///
/// Since the client needs to be configured correctly, don't use
/// [`pb::node_client::NodeClient`] directly, rather use
/// [`node::Node`] to create a correctly configured client.
pub mod pb;

/// Register, recover and schedule your nodes on greenlight.
pub mod scheduler;

/// Your keys, your coins!
///
/// This module implements the logic to stream, verify and respond to
/// signature requests from the node. Without this the node cannot
/// move your funds.
pub mod signer;

/// Helpers to configure the mTLS connection authentication.
///
/// mTLS configuration for greenlight clients. Clients are
/// authenticated by presenting a valid mTLS certificate to the
/// node. Each node has its own CA. This CA is used to sign both the
/// device certificates, as well as the node certificate itself. This
/// ensures that only clients that are authorized can open a
/// connection to the node.
pub mod tls;

/// Tools to interact with a node running on greenlight.
pub mod utils {

    pub fn scheduler_uri() -> String {
        match std::env::var("GL_SCHEDULER_GRPC_URI") {
            Ok(var) => {
                if std::path::Path::new(&var).is_file() {
                    std::fs::read_to_string(&var).expect(&format!(
                        "could not read file {} for envvar GL_SCHEDULER_GRPC_URI",
                        var
                    ))
                } else {
                    var
                }
            }
            Err(_) => "https://scheduler.gl.blckstrm.com:2601".to_string(),
        }
    }
}

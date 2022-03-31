# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import scheduler_pb2 as scheduler__pb2


class SchedulerStub(object):
    """The scheduler service is the endpoint which allows users to
    register a new node with greenlight, recover access to an existing
    node if the owner lost its credentials, schedule the node to be run
    on greenlight's infrastructure, and retrieve metadata about the
    node.

    Node
    ====

    A node is the basic object representing an account on
    greenlight. Each node corresponds to a c-lightning instance bound
    to a specific network that can be scheduled on greenlight, and must
    have a unique `node_id`.

    Nodes are scheduled on-demand onto the infrastructure, but the time
    to schedule a node is almost instantaneous.

    Authentication
    ==============

    Users are authenticated using mTLS authentication. Applications are
    provisioned with an anonymous keypair that is not bound to a node,
    allowing access only to the unauthenticated endpoints
    `Scheduler.GetChallenge`, `Scheduler.Register` and
    `Scheduler.Recover`. This allows them to register or recover a
    node, but doesn't give access to the node itself. Upon registering
    or recovering an account the user receives a keypair that is bound
    to the specific node. Once the user receives their personal mTLS
    keypair they may use it to connect to greenlight, and thus get
    access to the node-specific functionality. Please refer to the
    documentation of your grpc library to learn how to configure grpc
    to use the node-specific mTLS keypair.

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/scheduler.Scheduler/Register',
                request_serializer=scheduler__pb2.RegistrationRequest.SerializeToString,
                response_deserializer=scheduler__pb2.RegistrationResponse.FromString,
                )
        self.Recover = channel.unary_unary(
                '/scheduler.Scheduler/Recover',
                request_serializer=scheduler__pb2.RecoveryRequest.SerializeToString,
                response_deserializer=scheduler__pb2.RecoveryResponse.FromString,
                )
        self.GetChallenge = channel.unary_unary(
                '/scheduler.Scheduler/GetChallenge',
                request_serializer=scheduler__pb2.ChallengeRequest.SerializeToString,
                response_deserializer=scheduler__pb2.ChallengeResponse.FromString,
                )
        self.Schedule = channel.unary_unary(
                '/scheduler.Scheduler/Schedule',
                request_serializer=scheduler__pb2.ScheduleRequest.SerializeToString,
                response_deserializer=scheduler__pb2.NodeInfoResponse.FromString,
                )
        self.GetNodeInfo = channel.unary_unary(
                '/scheduler.Scheduler/GetNodeInfo',
                request_serializer=scheduler__pb2.NodeInfoRequest.SerializeToString,
                response_deserializer=scheduler__pb2.NodeInfoResponse.FromString,
                )
        self.MaybeUpgrade = channel.unary_unary(
                '/scheduler.Scheduler/MaybeUpgrade',
                request_serializer=scheduler__pb2.UpgradeRequest.SerializeToString,
                response_deserializer=scheduler__pb2.UpgradeResponse.FromString,
                )


class SchedulerServicer(object):
    """The scheduler service is the endpoint which allows users to
    register a new node with greenlight, recover access to an existing
    node if the owner lost its credentials, schedule the node to be run
    on greenlight's infrastructure, and retrieve metadata about the
    node.

    Node
    ====

    A node is the basic object representing an account on
    greenlight. Each node corresponds to a c-lightning instance bound
    to a specific network that can be scheduled on greenlight, and must
    have a unique `node_id`.

    Nodes are scheduled on-demand onto the infrastructure, but the time
    to schedule a node is almost instantaneous.

    Authentication
    ==============

    Users are authenticated using mTLS authentication. Applications are
    provisioned with an anonymous keypair that is not bound to a node,
    allowing access only to the unauthenticated endpoints
    `Scheduler.GetChallenge`, `Scheduler.Register` and
    `Scheduler.Recover`. This allows them to register or recover a
    node, but doesn't give access to the node itself. Upon registering
    or recovering an account the user receives a keypair that is bound
    to the specific node. Once the user receives their personal mTLS
    keypair they may use it to connect to greenlight, and thus get
    access to the node-specific functionality. Please refer to the
    documentation of your grpc library to learn how to configure grpc
    to use the node-specific mTLS keypair.

    """

    def Register(self, request, context):
        """A user may register a new node with greenlight by providing
        some basic metadata and proving that they have access to
        the corresponding private key (see challenge-response
        mechanism below). This means that in order to register a
        new node the user must have access to the corresponding
        private keys to prove ownership, and prevent users from
        just registering arbitrary node_ids without actually
        knowing the corresponding secrets.

        Upon successful registration an mTLS certificate and
        private key are returned. These can be used to authenticate
        future connections to the scheduler or the node.

        Each node may be registered once, any later attempt will
        result in an error being returned. If the user lost its
        credentials it can make use of the Recover RPC method to
        recover the credentials. Notice that this also means that
        the same node_id cannot be reused for different networks.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Recover(self, request, context):
        """Should a user have lost its credentials (mTLS keypair) for
        any reason, they may regain access to their node using the
        Recover RPC method. Similar to the initial registration the
        caller needs to authenticate the call by proving access to
        the node's secret. This also uses the challenge-response
        mechanism.

        Upon success a newly generated mTLS certificate and private
        key are returned, allowing the user to authenticate going
        forward. Existing keypairs are not revoked, in order to
        avoid locking out other authenticated applications.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetChallenge(self, request, context):
        """Challenges are one-time values issued by the server, used
        to authenticate a user/device against the server. A user or
        device can authenticate to the server by signing the
        challenge and returning the signed message as part of the
        request that is to be authenticated.

        Challenges may not be reused, and are bound to the scope
        they have been issued for. Attempting to reuse a challenge
        or use a challenge with a different scope will result in an
        error being returned.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Schedule(self, request, context):
        """Scheduling takes a previously registered node, locates a
        free slot in greenlight's infrastructure and allocates it
        to run the node. The node then goes through the startup
        sequence, synchronizing with the blockchain, and finally
        binding its grpc interface (see Node service below) to a
        public IP address and port. Access is authenticated via the
        mTLS keypair the user received from registering or
        recovering the node.

        Upon success a NodeInfoResponse containing the grpc
        connection details and some metadata is returned. The
        application must use the grpc details and its node-specific
        mTLS keypair to interact with the node directly.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNodeInfo(self, request, context):
        """Much like `Schedule` this call is used to retrieve the
        metadata and grpc details of a node. Unlike the other call
        however it is passive, and will not result in the node
        being scheduled if it isn't already running. This can be
        used to check if a node is already scheduled, or to wait
        for it to be scheduled (e.g., if the caller is an `hsmd`
        that signs off on changes, but doesn't want to keep the
        node itself scheduled).
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def MaybeUpgrade(self, request, context):
        """The signer may want to trigger an upgrade of the node
        before waiting for the node to be scheduled. This ensures
        that the signer version is in sync with the node
        version. The scheduler may decide to defer upgrading if the
        protocols are compatible. Please do not use this directly,
        rather use the Signer in the client library to trigger this
        automatically when required. Posting an incomplete or
        non-functional UpgradeRequest may result in unschedulable
        nodes.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SchedulerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=scheduler__pb2.RegistrationRequest.FromString,
                    response_serializer=scheduler__pb2.RegistrationResponse.SerializeToString,
            ),
            'Recover': grpc.unary_unary_rpc_method_handler(
                    servicer.Recover,
                    request_deserializer=scheduler__pb2.RecoveryRequest.FromString,
                    response_serializer=scheduler__pb2.RecoveryResponse.SerializeToString,
            ),
            'GetChallenge': grpc.unary_unary_rpc_method_handler(
                    servicer.GetChallenge,
                    request_deserializer=scheduler__pb2.ChallengeRequest.FromString,
                    response_serializer=scheduler__pb2.ChallengeResponse.SerializeToString,
            ),
            'Schedule': grpc.unary_unary_rpc_method_handler(
                    servicer.Schedule,
                    request_deserializer=scheduler__pb2.ScheduleRequest.FromString,
                    response_serializer=scheduler__pb2.NodeInfoResponse.SerializeToString,
            ),
            'GetNodeInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNodeInfo,
                    request_deserializer=scheduler__pb2.NodeInfoRequest.FromString,
                    response_serializer=scheduler__pb2.NodeInfoResponse.SerializeToString,
            ),
            'MaybeUpgrade': grpc.unary_unary_rpc_method_handler(
                    servicer.MaybeUpgrade,
                    request_deserializer=scheduler__pb2.UpgradeRequest.FromString,
                    response_serializer=scheduler__pb2.UpgradeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'scheduler.Scheduler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Scheduler(object):
    """The scheduler service is the endpoint which allows users to
    register a new node with greenlight, recover access to an existing
    node if the owner lost its credentials, schedule the node to be run
    on greenlight's infrastructure, and retrieve metadata about the
    node.

    Node
    ====

    A node is the basic object representing an account on
    greenlight. Each node corresponds to a c-lightning instance bound
    to a specific network that can be scheduled on greenlight, and must
    have a unique `node_id`.

    Nodes are scheduled on-demand onto the infrastructure, but the time
    to schedule a node is almost instantaneous.

    Authentication
    ==============

    Users are authenticated using mTLS authentication. Applications are
    provisioned with an anonymous keypair that is not bound to a node,
    allowing access only to the unauthenticated endpoints
    `Scheduler.GetChallenge`, `Scheduler.Register` and
    `Scheduler.Recover`. This allows them to register or recover a
    node, but doesn't give access to the node itself. Upon registering
    or recovering an account the user receives a keypair that is bound
    to the specific node. Once the user receives their personal mTLS
    keypair they may use it to connect to greenlight, and thus get
    access to the node-specific functionality. Please refer to the
    documentation of your grpc library to learn how to configure grpc
    to use the node-specific mTLS keypair.

    """

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/Register',
            scheduler__pb2.RegistrationRequest.SerializeToString,
            scheduler__pb2.RegistrationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Recover(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/Recover',
            scheduler__pb2.RecoveryRequest.SerializeToString,
            scheduler__pb2.RecoveryResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetChallenge(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/GetChallenge',
            scheduler__pb2.ChallengeRequest.SerializeToString,
            scheduler__pb2.ChallengeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Schedule(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/Schedule',
            scheduler__pb2.ScheduleRequest.SerializeToString,
            scheduler__pb2.NodeInfoResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetNodeInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/GetNodeInfo',
            scheduler__pb2.NodeInfoRequest.SerializeToString,
            scheduler__pb2.NodeInfoResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def MaybeUpgrade(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scheduler.Scheduler/MaybeUpgrade',
            scheduler__pb2.UpgradeRequest.SerializeToString,
            scheduler__pb2.UpgradeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

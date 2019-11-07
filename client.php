<?

class SocketError extends Exception {};
class ConnectionError extends Exception {};


class JsonRPC 
{
    private $hostname;
    private $port;
    private $id;

    function __construct($hostname, $port)
    {
        $this->hostname = $hostname;
        $this->port = $port;
        $this->id = 0;
    }

    private function getId() {
        return $this->id++;
    }

    function __call($name, $arguments)
    {

        $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        if ($socket === false) {
            throw SocketError;
        }
        // TODO: cache socket handle
        socket_set_option($socket, SOL_SOCKET, SO_RCVTIMEO, array('sec' => 1, 'usec' => 0));
        socket_set_option($socket, SOL_SOCKET, SO_SNDTIMEO, array('sec' => 1, 'usec' => 0));
        $result = socket_connect($socket, $this->hostname, $this->port);
        if ($result === false) {
            throw ConnectionError;
        }
        $payload = array(
            jsonrpc=>"2.0",
            method=>$name,
            params=>$arguments,
            id=>$this->getId()
        );

        $data = json_encode($payload);
        socket_write($socket, $data . "\n");
        $response = '';
        while ($out = socket_read($socket, 4096, PHP_NORMAL_READ)) {
            $response .= $out;
            if (substr($out, -1) === "\n") {
                break;
            }
        }
        socket_close($socket);
        return json_decode($response)->result;
    }
}


$rpc = new JsonRPC('127.0.0.1', 31337);
print_r($rpc->config("app"));
echo "\n";
?>

+-------------------------------------+
|          TCP vs. UDP Comparison     |
+--------------------+-------+--------+
| Feature            | TCP   | UDP    |
+--------------------+-------+--------+
| Connection         | Yes   | No     |
|                    | (Handshake) | (Direct Send) |
+--------------------+-------+--------+
| Reliability        | High  | Low    |
|                    | (ACKs, Retransmit) | (No Checks) |
+--------------------+-------+--------+
| Speed              | Slower| Faster |
|                    | (Overhead) | (Lightweight) |
+--------------------+-------+--------+
| Data Order         | Ordered | Unordered |
|                    | (Sequenced) | (Any Order) |
+--------------------+-------+--------+
| Flow Control       | Yes   | No     |
|                    | (Windowing) | (None) |
+--------------------+-------+--------+
| Use Cases          | Web, Email | Streaming, Games |
|                    | FTP       | DNS    |
+--------------------+-------+--------+
| Header Size        | 20-60B| 8B     |
|                    | (Complex) | (Simple) |
+--------------------+-------+--------+
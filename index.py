from app import app

import callbacks.highlight_nodes
import callbacks.filter_nodes
import callbacks.group_nodes

if __name__ == "__main__":
    app.run_server(debug=True)

// non-recursive javascript program for inorder traversal

/* Class containing left and right child of
current node and key value*/
class Node {
  constructor(item) {
    this.data = item;
    this.left = this.right = null;
  }
}

/* Class to print the inorder traversal */

var root;

function inorder() {
  if (root == null) return;

  var s = [];
  var curr = root;

  // traverse the tree
  while (curr != null || s.length > 0) {
    /*
     * Reach the left most Node of the curr Node
     */
    while (curr != null) {
      /*
       * place pointer to a tree node on the stack before traversing the node's left
       * subtree
       */
      s.push(curr);
      curr = curr.left;
    }

    /* Current must be NULL at this point */
    curr = s.pop();

    console.log(curr.data);

    /*
     * we have visited the node and its left subtree. Now, it's right subtree's turn
     */
    curr = curr.right;
  }
}

/*
 * creating a binary tree and entering the nodes
 */
root = new Node(1);
root.left = new Node(2);
root.right = new Node(3);
root.left.left = new Node(4);
root.left.right = new Node(5);
inorder();

// This code is contributed by umadevi9616

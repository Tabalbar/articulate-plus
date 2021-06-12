import React from 'react'
import TreeMenu from 'react-simple-tree-menu'
import '../../node_modules/react-simple-tree-menu/dist/main.css';


function Attributes() {
    return (
        <>
              <TreeMenu data={treeData} />
        </>
    )
}



export default Attributes

const treeData = [
    {
      key: 'first-level-node-1',
      label: 'Node 1 at the first level',
      nodes: [
        {
          key: 'second-level-node-1',
          label: 'Node 1 at the second level',
          nodes: [
            {
              key: 'third-level-node-1',
              label: 'Last node of the branch',
              nodes: [] // you can remove the nodes property or leave it as an empty array
            },
          ],
        },
      ],
    },
    {
        key: 'first-level-node-1',
        label: 'Node 1 at the first level',
        nodes: [
          {
            key: 'second-level-node-1',
            label: 'Node 1 at the second level',
            nodes: [
              {
                key: 'third-level-node-1',
                label: 'Last node of the branch',
                nodes: [] // you can remove the nodes property or leave it as an empty array
              },
            ],
          },
        ],
      },
      {
        key: 'first-level-node-1',
        label: 'Node 1 at the first level',
        nodes: [
          {
            key: 'second-level-node-1',
            label: 'Node 1 at the second level',
            nodes: [
              {
                key: 'third-level-node-1',
                label: 'Last node of the branch',
                nodes: [] // you can remove the nodes property or leave it as an empty array
              },
            ],
          },
        ],
      },
      {
        key: 'first-level-node-1',
        label: 'Node 1 at the first level',
        nodes: [
          {
            key: 'second-level-node-1',
            label: 'Node 1 at the second level',
            nodes: [
              {
                key: 'third-level-node-1',
                label: 'Last node of the branch',
                nodes: [] // you can remove the nodes property or leave it as an empty array
              },
            ],
          },
        ],
      },
    {
      key: 'first-level-node-2',
      label: 'Node 2 at the first level',
    },
  ];
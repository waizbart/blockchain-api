// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AnonymousReports {
    struct Report {
        string reportHash;  
        uint256 timestamp;
    }

    Report[] public reports;

    event NewReport(uint256 reportId, string reportHash, uint256 timestamp);

    function addReport(string memory _reportHash) public {
        reports.push(Report({
            reportHash: _reportHash,
            timestamp: block.timestamp
        }));
        emit NewReport(reports.length - 1, _reportHash, block.timestamp);
    }

    function getReportCount() public view returns (uint256) {
        return reports.length;
    }
}

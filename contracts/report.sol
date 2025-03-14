// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DenunciaAnonima {
    struct Denuncia {
        string hashDados;
        uint256 dataHora;
        string categoria;
    }

    Denuncia[] public denuncias;

    function registrarDenuncia(string memory _hashDados, string memory _categoria) public {
        denuncias.push(Denuncia(_hashDados, block.timestamp, _categoria));
    }

    function obterTotalDenuncias() public view returns(uint256) {
        return denuncias.length;
    }

    function obterDenuncia(uint256 id) public view returns(Denuncia memory) {
        return denuncias[id];
    }
}
